from datetime import datetime
from flask import Flask, make_response
from icalendar import Calendar, Event
import re
import requests
import uuid
from zoneinfo import ZoneInfo

url = "https://embed.creek.org/api/studio/schedule?studioId=84"

r = requests.get(url)
shows = r.json()

def make_dt_time(date_time):
    tz = ZoneInfo("America/New_York")
    dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)

def rrule_clean(rrule_in):
    dtstart, rrule = (rrule_in).split("\n")
    rrule = rrule.split(":")[1]
    return rrule


flask_app = Flask("radiocal")
@flask_app.route('/radiocal/', methods=['GET'], defaults={'show': ''})
@flask_app.route("/radiocal/<string:show>", methods=['GET'])
def radiocal(show):
    cal = Calendar()
    #cal.add('X-WR-CALNAME', f'WOBC Calendar')
    #cal.add('name', 'WOBC Calendar')
    cal.add('prodid', '-//WOBC//WOBC Calendar//EN')
    cal.add('version', '2.0')

    showcounter = 0

    for entry in shows:
        if entry == "" or show.lower() in entry["time"]["show"]["title"].lower():

            showname = entry["time"]["show"]["title"]

            event = Event()
            event.add('rrule', rrule_clean(entry["time"]["rrule"]))
            event.add('dtstart', make_dt_time(entry["time"]["start"]))
            event.add('dtend', make_dt_time(entry["time"]["end"]))
            event.add('summary', entry["time"]["show"]["title"])
            event.add('description', entry["time"]["show"]["description"])
            event.add('url', f"https://wobcfm.org/shows/{entry['time']['show']['name']}", parameters={"value": "URI"})
            event.add('dtstamp', make_dt_time(entry["time"]["show"]["updated_at"]))
            event.add('tzid', 'America/New_York')
            event.add('uid', str(uuid.uuid1()) + "@puskar.net")
            cal.add_component(event)

            showcounter += 1
        else:
            continue

    if showcounter == 1:
        cal.add('X-WR-CALNAME', f'WOBC {showname} Calendar')
        cal.add('name', f'WOBC {showname} Calendar')
    else:
        cal.add('X-WR-CALNAME', 'WOBC Calendar')
        cal.add('name', 'WOBC Calendar')

    ics = cal.to_ical().decode("utf-8").replace('\r\n', '\n').strip()
    response = make_response(ics)
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    return response

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8090, debug=True)
