#Talking weather for Raspberry Pi
Audible messages regarding weather conditions and calendar events using Google TTS (Text To Speech) and Wunderground weather API.
##Options
Play audible message regarding weather conditions and calendar events:
```
python pogoda.py --typical
```
Play audible message regarding current time:
```
python pogoda.py --time
```
##Usage
Add folowing entries to crontab by running
```
crontab -e
```
```
30 7,9,11,13,15,17,19,21,23 * * * python /home/pi/moje/python/pogoda/pogoda.py --typical >/dev/null 2>&1
00 8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24 * * * python /home/pi/moje/python/pogoda/pogoda.py --time >/dev/null 2>&1
```
##Author
Kamil Cyrkler
