import pandas as pd
import uuid
from icalendar import Calendar, Event
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from flask import Flask, make_response, render_template

url = "https://wobc.pairsite.com/?O=&I=&P=16&InfoID=3&P=17&B=Schedule"
file_url = "file:////Users/puskar/workspace/github/odds_ends/radiocal/radio.html"

# Cache the DataFrame at startup
table = pd.read_html(url, header=0, index_col=0)
df_cached = table[0]

flask_app = Flask("radiocal")
@flask_app.route('/radiocal/', methods=['GET'], defaults={'show': ''})
@flask_app.route("/radiocal/<string:show>", methods=['GET'])
def radiocal(show):
    df = df_cached

    today = datetime.now()
    today = today.replace(tzinfo=ZoneInfo("America/New_York"))
    tz= ZoneInfo("America/New_York")

    cal = Calendar()
    cal.add('X-WR-CALNAME', 'WOBC calendar')
    cal.add('prodid', '-//WOBC//WOBC Calendar//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-TIMEZONE', 'America/New_York')
    cal.add('tzid', tz)

    sunday = today - timedelta(days=today.isoweekday())

    x=0
    for col in df.columns:
        y=0

        for item in df[col]:
            showtime = df[col].index[y]

            if showtime == "Midnight":
                showtime = "12am"
            elif showtime == "Noon":
                showtime = "12pm"

            if show == "" or show.lower() in item.lower():
            #print(f'col={col}')
            #print(f'Hour: {showtime:>04} Show: {item}')

                sdate = sunday + timedelta(days=x)
                #print(f'sdate={sdate}')
                stime= datetime.strptime(f'{showtime:>04}', "%I%p")
                #print(f'stime={stime}' )
                show_date = datetime.combine(sdate, stime.time(), tzinfo=tz)
                event = Event()
                #event['dtstart'] = show_date.strftime('%Y%m%dT%H%M00')
                event.add('dtstart', show_date)
                event.add('uid', str(uuid.uuid1()) + "@puskar.net")
                event.add('dtstamp', datetime.now(tz=ZoneInfo("UTC")))
                event.add('summary', item)
                event.add('dtend', show_date + timedelta(hours=1))
                cal.add_component(event)
            else:
                continue
            #print(f'show_date={show_date}')
            #print("\r")

            y += 1
        x += 1
        response = make_response(cal.to_ical().decode("utf-8").replace('\r\n', '\n').strip())
        response.headers['Content-Type'] = 'text/calendar'
        #response.headers['Content-Disposition'] = f'inline; filename="{part1.title() or "WOBC"}.ics"'


    return response


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8090, debug=True)
