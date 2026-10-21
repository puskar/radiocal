from datetime import datetime
from flask import make_response, Blueprint
from icalendar import Calendar, Event
import requests
import uuid
from zoneinfo import ZoneInfo

url = "https://embed.creek.org/api/studio/schedule?studioId=84"

r = requests.get(url)
shows = r.json()


def make_dt_time(date_time):
    """Convert a date_time string to a timezone-aware datetime object in the America/New_York timezone."""
    tz = ZoneInfo("America/New_York")
    dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)


def rrule_clean(rrule_in):
    """Clean the rrule string by extracting the relevant part after the "RRULE:" prefix."""
    dtstart, rrule = (rrule_in).split("\n")
    rrule = rrule.split(":")[1]
    return rrule

wobc_bp = Blueprint('wobc', __name__)

@wobc_bp.route("/wobc/", methods=["GET"], defaults={"show": ""})
@wobc_bp.route("/wobc/<string:show>", methods=["GET"])
def radiocal(show):
    cal = Calendar()
    cal.add("prodid", "-//WOBC//WOBC Calendar//EN")
    cal.add("version", "2.0")

    showlist = set()

    for entry in shows:
        if entry == "" or show.lower() in entry["time"]["show"]["title"].lower():
            showname = entry["time"]["show"]["title"]

            event = Event()
            event.add("rrule", rrule_clean(entry["time"]["rrule"]))
            event.add("dtstart", make_dt_time(entry["time"]["start"]))
            event.add("dtend", make_dt_time(entry["time"]["end"]))
            event.add("summary", entry["time"]["show"]["title"])
            event.add("description", entry["time"]["show"]["description"])
            event.add(
                "url",
                f"https://wobcfm.org/shows/{entry['time']['show']['name']}",
                parameters={"value": "URI"},
            )
            event.add("dtstamp", make_dt_time(entry["time"]["show"]["updated_at"]))
            event.add("tzid", "America/New_York")
            event.add("uid", str(uuid.uuid1()) + "@puskar.net")
            cal.add_component(event)

            showlist.add(showname)
        else:
            continue

    if len(showlist) == 1:
        for s_name in showlist:
            cal.add("X-WR-CALNAME", f"WOBC {s_name} Calendar")
            cal.add("name", f"WOBC {s_name} Calendar")

    else:
        cal.add("X-WR-CALNAME", "WOBC Calendar")
        cal.add("name", "WOBC Calendar")

    cal.add_missing_timezones()

    ics = cal.to_ical().decode("utf-8").replace("\r\n", "\n").strip()
    response = make_response(ics)
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response

