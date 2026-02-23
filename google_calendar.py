import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

creds = Credentials(
    None,
    refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
)

service = build("calendar", "v3", credentials=creds)

def create_event(name, date, time):
    start = datetime.fromisoformat(f"{date}T{time}")
    end = start + timedelta(minutes=30)

    event = {
        "summary": f"Appointment with {name}",
        "start": {"dateTime": start.isoformat()},
        "end": {"dateTime": end.isoformat()},
    }

    service.events().insert(calendarId="primary", body=event).execute()
    