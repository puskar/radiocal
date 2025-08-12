## radiocal

This app scrapes the [WOBC](https://wobc.pairsite.com/?O=&I=&P=1&InfoID=3&P=17&B=Schedule) schedule page and creates a calendar of the radio shows for the week. It uses Flask to provide a web service that can be subscribed from any calendar app. It runs at the endpoint```/radiocal/```

Appending a string will perform a case insensitive match for shows that contain the string, e.g. ```/radiocal/ha``` will show the calendar for "Chains and Things" and "Chameleon Radio ⊳".
