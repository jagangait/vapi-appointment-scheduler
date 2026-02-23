from sqlalchemy.orm import Session
from models import Appointment

def check_availability(db: Session, date: str, time: str):
    appointment = db.query(Appointment).filter_by(date=date, time=time).first()
    return appointment is None

def book_appointment(db: Session, name, phone, date, time):
    new_appt = Appointment(name=name, phone=phone, date=date, time=time)
    db.add(new_appt)
    db.commit()
    