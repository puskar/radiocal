from bs4 import BeautifulSoup
import pandas as pd
import requests
from icalendar import Calendar, Event
from datetime import date, datetime, time, timedelta, timezone

url = "https://wobc.pairsite.com/?O=&I=&P=16&InfoID=3&P=17&B=Schedule"
file_url = "file:////Users/puskar/workspace/github/odds_ends/radiocal/radio.html"

r = requests.get(url)


#with open("/Users/puskar/Desktop/radio.html", "r") as f:
#    html_doc=f.read()
#html_doc = r.text
#soup = BeautifulSoup(html_doc, 'html.parser')
#table = soup.find("table")


#d = datetime.strptime(time, "%Y-%m-%d %H:%M").strftime('%Y%m%dT%H%M00Z')

table = pd.read_html(url, header=0, index_col=0)
#table = pd.read_html(file_url, header=0, index_col=0)
df = table[0]


#print(dir(df))
#print(df)

#tue = df['Tuesday', None]


#for col in df.columns:
#    if isinstance(col, tuple):
#        col = ' '.join(map(str, col))
#        print(col)


cal = Calendar()
cal.add('X-WR-CALNAME', 'WOBC calendar')

today =datetime.now()


sunday = today - timedelta(days=today.isoweekday())

print(f'{sunday=}')

print(df)
x=0
for col in df.columns:
    y=0

    for item in df[col]:
        showtime = df[col].index[y]

        if showtime == "Midnight":
            showtime = "12am"
        elif showtime == "Noon":
            showtime = "12pm"

        print(f'col={col}')
        print(f'Hour: {showtime:>04} Show: {item}')
        
        sdate = sunday + timedelta(days=x)
        stime= datetime.strptime(f'{showtime:>04}', "%I%p")
        show_date = datetime.combine(sdate, stime.time())
        event = Event()
        event['dtstart'] = show_date.strftime('%Y%m%dT%H%M00Z')
        event['summary'] = item
        event['dtend'] = (show_date + timedelta(hours=1)).strftime('%Y%m%dT%H%M00Z')
        cal.add_component(event)
        
        print(f'show_date={show_date}')
        print("\r")
              
        y += 1      
    x += 1

print(cal.to_ical().decode('utf-8'))


