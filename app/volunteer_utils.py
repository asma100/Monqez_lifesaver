from datetime import datetime
from app.models import Volunteer
from app import db
from datetime import datetime

def get_all_available_volunteers():
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")
    current_time_obj = datetime.strptime(current_time, "%H:%M").time()

    volunteers = Volunteer.query.all()
    available = []

    print(volunteers)

    for v in volunteers:
        if current_day in v.available_days:
            print("day is available")
            try:
                start_str, end_str = v.available_times.split("-")
                start_time = datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M").time()
                print(start_time, end_time, current_time_obj)

                if start_time < end_time:
                    # Regular time range (e.g., 08:00-12:00)
                    if start_time <= current_time_obj <= end_time:
                        available.append(v)
                else:
                    # Time range spans midnight (e.g., 20:00-00:00)
                    if current_time_obj >= start_time or current_time_obj <= end_time:
                        available.append(v)

            except ValueError:
                continue

    print(available)
    return available
