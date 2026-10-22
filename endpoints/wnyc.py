from datetime import datetime
from flask import make_response, Blueprint
from icalendar import Calendar, Event
import requests
import uuid
from zoneinfo import ZoneInfo

url = "https://wnyc.org/api/schedule/wnyc-fm939"

r = requests.get(url)
shows = r.json()


def make_dt_time(date_time):
    """Convert a date_time string to a timezone-aware datetime object in the America/New_York timezone."""
    tz = ZoneInfo("America/New_York")
    dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
    return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)


def rrule_clean(rrule_in):
    """Clean the rrule string by extracting the relevant part after the "RRULE:" prefix."""
    dtstart, rrule = (rrule_in).split("\n")
    rrule = rrule.split(":")[1]
    return rrule


wnyc_bp = Blueprint("wnyc", __name__)


@wnyc_bp.route("/wnyc/", methods=["GET"], defaults={"show": ""})
@wnyc_bp.route("/wnyc/<string:show>", methods=["GET"])
def radiocal(show):
    cal = Calendar()
    cal.add("prodid", "-//WNYC//WNYC Calendar//EN")
    cal.add("version", "2.0")

    showlist = set()

    for entry in shows:
        if entry == "" or show.lower() in entry["attributes"]["parentTitle"].lower():
            showname = entry["attributes"]["parentTitle"]

            event = Event()
            # event.add("rrule", rrule_clean(entry["time"]["rrule"]))
            event.add("dtstart", make_dt_time(entry["attributes"]["start"]))
            event.add("dtend", make_dt_time(entry["attributes"]["end"]))
            event.add("summary", entry["attributes"]["parentTitle"])
            event.add("description", entry["attributes"]["longDescription"])
            event.add(
                "url",
                f"{entry['attributes']['parentUrl']}",
                parameters={"value": "URI"},
            )
            event.add("dtstamp", make_dt_time(entry["attributes"]["start"]))
            event.add("tzid", "America/New_York")
            event.add(
                "uid",
                str(uuid.uuid5(uuid.NAMESPACE_DNS, (str(event.DTSTART) + showname)))
                + "@puskar.net",
            )
            cal.add_component(event)

            showlist.add(showname)
        else:
            continue

    if len(showlist) == 1:
        for s_name in showlist:
            cal.add("X-WR-CALNAME", f"WNYC {s_name} Calendar")
            cal.add("name", f"WNYC {s_name} Calendar")

    else:
        cal.add("X-WR-CALNAME", "WNYC Calendar")
        cal.add("name", "WNYC Calendar")

    cal.add_missing_timezones()

    ics = cal.to_ical().decode("utf-8").replace("\r\n", "\n").strip()
    response = make_response(ics)
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response
