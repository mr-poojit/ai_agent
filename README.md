# TailorTalk – AI Appointment Assistant

TailorTalk is a conversational AI agent that helps users schedule Google Calendar meetings using natural language. It uses Gemini 1.5 Flash for language understanding and integrates with Google Calendar via a service account.

---

## 🚀 Features

- 🧠 Natural language understanding using **Gemini (1.5 Flash)**
- 📅 Google Calendar integration for:
  - Checking availability
  - Booking meetings
  - Preventing duplicate bookings
- 💬 Interactive frontend using **Streamlit**
- 💡 Memory-aware behavior (avoids rebooking the same slot)
- 📎 Hyperlinked calendar invites

---

## 📁 Project Structure

```
TailorTalk/
│
├── backend/
│   ├── main.py               # FastAPI app entrypoint
│   ├── graph.py              # LangGraph with tool nodes
│   ├── calender_utils.py     # Google Calendar logic (get slots + create event)
│   ├── creds.json            # Service account credentials (secure this!)
│   └── requirements.txt      # Backend dependencies
│
├── frontend/
│   └── app.py                # Streamlit UI for chat interface
│
├── .env                      # Environment variables (API keys, URLs)
├── README.md                 # You're here!
```

---

## ⚙️ Requirements

- Python 3.10+
- Google Cloud service account with Calendar API enabled
- Gemini API Key (https://aistudio.google.com/app/apikey)
- Optional: Render.com or Streamlit Cloud for deployment

---

## 🛠️ Installation

1. **Clone the repo**

```bash
git clone https://github.com/mr-poojit/tailortalk.git
cd tailortalk
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. **Install dependencies**

```bash
pip install -r backend/requirements.txt
```

4. **Set environment variables in `.env`**

```env
GEMINI_API_KEY=your_google_gemini_api_key
GOOGLE_CREDS_PATH=backend/creds.json
BACKEND_URL=http://localhost:8000/chat
```

---

## 🔐 Setup Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account and download `creds.json`
3. Share your calendar with the service account email
4. Place `creds.json` inside `backend/`

---

## ▶️ Run the App Locally

### Start the backend (FastAPI):

```bash
cd backend
uvicorn main:app --reload
```

### Start the frontend (Streamlit):

```bash
cd frontend
streamlit run app.py
```

---

## 🌍 Deployment

### Option 1: **Render.com**

- Create 2 services:
  - One for backend (`uvicorn main:app --host 0.0.0.0 --port 10000`)
  - One for frontend (`streamlit run app.py`)
- Set environment variables in Render dashboard
- Update `BACKEND_URL` in frontend `.env` to the Render backend URL

### Option 2: **Streamlit Community Cloud**

- Push `frontend/app.py` to GitHub
- Deploy via https://streamlit.io/cloud

---

## 📸 Screenshots

> _Add screenshots of chat interface, scheduled meeting view, etc._

---

## 📌 Example Prompts

```
Hi, I want to book a meeting tomorrow at 3pm called "Demo Call"
Check my availability
Schedule a meeting on 10th July at 11am titled "Team Sync"
```

---

## 🧠 Tech Stack

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Gemini API (Google AI Studio)](https://aistudio.google.com/)
- [Google Calendar API](https://developers.google.com/calendar)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)

---

## 📄 License

MIT License. Feel free to fork and use.
