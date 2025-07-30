from datetime import datetime
from app.models import Volunteer
import random

def get_available_volunteer():
    now = datetime.now()
    today = now.strftime("%A")  # e.g., "Saturday"
    current_time = now.strftime("%H:%M")

    volunteers = Volunteer.query.all()
    available = []

    for v in volunteers:
        if today in v.available_days:
            start, end = v.available_times.split("-")
            if start <= current_time <= end:
                available.append(v)

    if not available:
        return None

    # Simple load balancing: sort by last_assigned
    available.sort(key=lambda x: x.last_assigned or datetime.min)
    selected = available[0]
    selected.last_assigned = datetime.now()
    db.session.commit()
    return selected
