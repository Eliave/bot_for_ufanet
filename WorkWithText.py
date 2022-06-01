from datetime import datetime, time

def time_1(text):
    try:
        new_time = datetime.strptime(text, "%H:%M %d.%m.%Y")
        return new_time
    except:
        return None
