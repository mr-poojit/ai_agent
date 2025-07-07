from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import pytz

SERVICE_ACCOUNT_FILE = 'creds.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'primary'  # Replace if using a shared calendar

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('calendar', 'v3', credentials=credentials)

# Get next few busy slots
def get_available_slots():
    now = datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
    events_result = service.events().list(
    calendarId=CALENDAR_ID,
    timeMin=now,
    maxResults=20,  # increase from 5
    singleEvents=True,
    orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

# Create a calendar event
def create_event(summary, start, end=None, attendee_email=""):
    event = {
        "summary": summary,
        "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end, "timeZone": "Asia/Kolkata"} if end else None,
    }

    if attendee_email:
        event["attendees"] = [{"email": attendee_email}]

    # Remove None fields for safety
    event = {k: v for k, v in event.items() if v is not None}

    try:
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return created_event
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return None

