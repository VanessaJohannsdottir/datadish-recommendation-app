from datetime import datetime
import calendar

def get_current_day_time():
    now = datetime.now()
    return now.strftime("%A"), now.strftime("%H:%M")

def is_open_now(hours_string):
    current_day, current_time = get_current_day_time()
    if not hours_string:
        return False

    entries = [e.strip() for e in hours_string.split(" · ")]
    for entry in entries:
        if current_day in entry:
            try:
                time_range = entry.split(": ", 1)[1]
                open_time, close_time = time_range.split("-")
                h_now = int(current_time[:2]) * 60 + int(current_time[3:])
                h_open = int(open_time[:2]) * 60 + int(open_time[3:])
                h_close = int(close_time[:2]) * 60 + int(close_time[3:])
                if h_close < h_open:
                    h_close += 1440  # über Mitternacht
                return h_open <= h_now <= h_close
            except:
                return False
    return False

def format_hours(hours_string):
    day_order = list(calendar.day_name)
    day_map = {day: "" for day in day_order}
    for entry in hours_string.split(" · "):
        if ": " in entry:
            day, time = entry.split(": ", 2)
            if day in day_map:
                day_map[day] = time
    return "\n".join([f"{day}: {day_map[day]}" for day in day_order if day_map[day]])