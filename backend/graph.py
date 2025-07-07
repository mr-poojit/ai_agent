import os
from dotenv import load_dotenv
from typing import List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from calender_utils import get_available_slots, create_event
from datetime import datetime, timedelta
import dateparser
import pytz

load_dotenv()

# Define shared memory format
class GraphState(TypedDict):
    messages: List[BaseMessage]

# 🛠️ Tool: Check availability
@tool
def check_availability() -> str:
    """Returns your next upcoming Google Calendar events."""
    events = get_available_slots()
    if not events:
        return "✅ You're free for the next few hours!"
    return "\n".join([f"{e['start']['dateTime']} - {e.get('summary', 'No Title')}" for e in events])

# 🛠️ Tool: Book a meeting
@tool
def book_meeting(summary: str, start_time: str, end_time: str = "", attendee_email: str = "") -> str:
    """
    Books a meeting in Google Calendar.
    Avoids booking over existing events. End time optional (defaults to 1 hour).
    """
    try:
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)

        parsed_start = dateparser.parse(start_time, settings={"TIMEZONE": "Asia/Kolkata", "RELATIVE_BASE": now})
        if not parsed_start:
            return "❌ Could not understand the start time."
        parsed_start = parsed_start.astimezone(tz)

        if end_time:
            parsed_end = dateparser.parse(end_time, settings={"TIMEZONE": "Asia/Kolkata", "RELATIVE_BASE": now})
            if not parsed_end:
                return "❌ Could not understand the end time."
            parsed_end = parsed_end.astimezone(tz)
        else:
            parsed_end = parsed_start + timedelta(hours=1)

        # 🧠 Conflict check
        events = get_available_slots()
        for event in events:
            try:
                start_str = event["start"].get("dateTime") or event["start"].get("date")
                end_str = event["end"].get("dateTime") or event["end"].get("date")
                existing_start = dateparser.parse(start_str)
                existing_end = dateparser.parse(end_str)

                if existing_start and existing_end:
                    if parsed_start < existing_end and parsed_end > existing_start:
                        return f"⚠️ You already have a meeting **'{event.get('summary', 'Untitled')}'** at that time."
            except Exception:
                continue

        # ✅ Book event
        event = create_event(summary, parsed_start.isoformat(), parsed_end.isoformat(), attendee_email)
        if not event:
            return "❌ Failed to create event. Please check your credentials or input format."

        return f"✅ Meeting booked!\n📅 [View in Google Calendar]({event.get('htmlLink', 'Link unavailable')})"
    except Exception as e:
        return f"❌ Error booking meeting: {str(e)}"

# Tool registry
tools = [check_availability, book_meeting]

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
).bind_tools(tools)

# 🔄 LangGraph Nodes

def process_node(state: GraphState) -> GraphState:
    system_message = HumanMessage(content="""
You are an AI calendar assistant that helps users schedule meetings using Google Calendar.

Behavior:
- If user says "book demo meeting tomorrow at 5pm", extract:
  - summary: 'demo meeting'
  - start_time: 'tomorrow at 5pm'
- Do NOT ask again if summary or time is already given.
- Book without end time if not given (default to 1hr).
- Include calendar link in final response if event is booked.
- If the user asks for "link", return the latest calendar link.

Instructions:
- Do not make up times.
- Use tools if time or summary is mentioned.
""")

    response = llm.invoke([system_message] + state["messages"])
    return {"messages": state["messages"] + [response]}

def tool_node(state: GraphState) -> GraphState:
    messages = state["messages"]
    tool_call = messages[-1].tool_calls[0]
    tool_name = tool_call["name"]
    args = tool_call["args"]

    tool = next(t for t in tools if t.name == tool_name)
    result = tool.invoke(args)

    tool_msg = ToolMessage(content=str(result), tool_call_id=tool_call["id"])
    return {"messages": messages + [tool_msg]}

def needs_tool(state: GraphState) -> str:
    last = state["messages"][-1]
    return "tool" if hasattr(last, "tool_calls") and last.tool_calls else "default"

# 🔧 Build LangGraph
workflow = StateGraph(GraphState)
workflow.add_node("process", process_node)
workflow.add_node("tool", tool_node)
workflow.set_entry_point("process")
workflow.add_conditional_edges("process", needs_tool, {"tool": "tool", "default": END})
workflow.add_edge("tool", "process")
graph = workflow.compile()
