from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
import os
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

app = FastAPI()

# ---------- DATABASE ----------
conn = sqlite3.connect("appointments.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    date TEXT,
    time TEXT
)
""")
conn.commit()

# ---------- GOOGLE CALENDAR ----------
creds = Credentials(
    None,
    refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
)

calendar = build("calendar", "v3", credentials=creds)

def create_event(name, date, time):
    start = datetime.fromisoformat(f"{date}T{time}")
    end = start + timedelta(minutes=30)

    event = {
        "summary": f"Appointment with {name}",
        "start": {"dateTime": start.isoformat()},
        "end": {"dateTime": end.isoformat()},
    }

    calendar.events().insert(calendarId="primary", body=event).execute()

# ---------- REQUEST MODEL ----------
class Booking(BaseModel):
    name: str
    phone: str
    date: str
    time: str

# ---------- ENDPOINT ----------
@app.post("/book")
def book(data: Booking):
    cursor.execute(
        "SELECT * FROM appointments WHERE date=? AND time=?",
        (data.date, data.time)
    )
    exists = cursor.fetchone()

    if exists:
        return {"available": False}

    cursor.execute(
        "INSERT INTO appointments(name, phone, date, time) VALUES(?,?,?,?)",
        (data.name, data.phone, data.date, data.time)
    )
    conn.commit()

    create_event(data.name, data.date, data.time)

    return {"available": True, "message": "Appointment booked"}

@app.get("/")
def home():
    return {"status": "running"}
