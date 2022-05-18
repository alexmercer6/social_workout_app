from datetime import datetime

def format_sleep_time(sleep_time):
    if len(sleep_time) > 0:
        nap_start = datetime.strptime(sleep_time[0][0], "%H:%M")
        nap_start = nap_start.strftime("%I:%M %p")

        nap_end = datetime.strptime(sleep_time[0][1], "%H:%M")
        nap_end =nap_end.strftime("%I:%M %p")
        return nap_start, nap_end
    else:
        nap_start = ''
        nap_end =''
        return nap_start, nap_end