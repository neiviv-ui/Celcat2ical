# Celcat2iCal
Small project I made to merge my multiple universary plannings :  
  
Since they're published in a proprietary format, I short-cut the publisher by directly calling the HTML methods I discovered diving in its code.  
The main file downloads all the raw calendar data I need then _parse, filter and merge_ them into a number of calendars, cleverly sorted by runtime detected categories ("CM" and "CM à distance" go to "CM").  
  
It finally pushes all those files to a nextcloud server, which my phone's calendar app can access.
