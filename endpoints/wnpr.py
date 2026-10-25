import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from flask import Blueprint, make_response
from icalendar import Calendar, Event


def get_shows():
    """Fetch the list of shows from the NPR Cadence API."""
    url = "https://cadence.nprstations.org//api/cadence/widget/"
    payload = {
        "channelId": "52b2d312-4f33-4d4e-a818-60330d61a4dc",
        "startDate": (datetime.today() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "endDate": (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "from": 0,
        "size": 10000,
    }

    r = requests.post(url, json=payload)
    return r.json()


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


wnpr_bp = Blueprint("wnpr", __name__)


@wnpr_bp.route("/wnpr/", methods=["GET"], defaults={"show": ""})
@wnpr_bp.route("/wnpr/<string:show>", methods=["GET"])
def radiocal(show):
    shows = get_shows()
    cal = Calendar()
    cal.add("prodid", "-//WNPR//WNPR Calendar//EN")
    cal.add("version", "2.0")

    showlist = set()

    for entry in shows["episodes"]:
        if entry == "" or show.lower() in entry["episode"]["programName"].lower():
            showname = entry["episode"]["programName"]

            event = Event()
            event.add("dtstart", make_dt_time(entry["episode"]["start"]["utc"]))
            event.add("dtend", make_dt_time(entry["episode"]["end"]["utc"]))
            event.add("summary", entry["episode"]["programName"])
            if "programDescription" in entry:
                event.add("description", entry["programDescription"])
            if "programLink" in entry:
                event.add(
                    "url",
                    f"{entry['programLink']}",
                    parameters={"value": "URI"},
                )
            event.add("dtstamp", make_dt_time(entry["episode"]["start"]["utc"]))
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
            cal.add("X-WR-CALNAME", f"WNPR {s_name} Calendar")
            cal.add("name", f"WNPR {s_name} Calendar")

    else:
        cal.add("X-WR-CALNAME", "WNPR Calendar")
        cal.add("name", "WNPR Calendar")

    cal.add_missing_timezones()

    ics = cal.to_ical().decode("utf-8").replace("\r\n", "\n").strip()
    response = make_response(ics)
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response
