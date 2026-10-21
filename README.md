## radiocal

Create calendar subscription feeds from radio station sources.

It uses Flask to provide a web service that can be subscribed from any calendar app. It runs at the endpoint```/radiocal/```

Currently supported stations are:

WNPR - [Connecticut Public Radio](https://ctpublic.org)     [feed](https://api.puskar.net/radiocal/wnpr/)  
WNYC - [New York Public Radio](https://wnyc.org)     [feed](https://api.puskar.net/radiocal/wnyc/)  
WOBC - [Oberlin College Radio](https://wobcfm.org)     [feed](https://api.puskar.net/radiocal/wobc/)  

Appending a string will perform a case insensitive match for shows that contain the string, e.g. ```/radiocal/wobc/ha``` will show the calendar for "Chains and Things" and "Chameleon Radio ⊳".  
```/radiocal/wnpr/colin``` will show the calendar for "The Colin McEnroe Show".
