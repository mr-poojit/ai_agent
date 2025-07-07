from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from utils.graph import graph
  

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

chat_history = []

@app.post("/chat")
async def chat(data: ChatRequest):
    global chat_history

    chat_history.append(HumanMessage(content=data.message))
    result = graph.invoke({"messages": chat_history})
    chat_history.append(result["messages"][-1])
    return {"response": result["messages"][-1].content}
