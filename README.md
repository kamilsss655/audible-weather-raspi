#Audible weather for Raspberry Pi
Audible messages regarding weather conditions and calendar events using Google TTS (Text To Speech) and Wunderground weather API.
##Dependencies
The mpg123 package is required to play messages. This script automatically stops music played by MPD deamon for the duration of the message and resumes playback after its done. Please make sure that you have following packages installed:
```
sudo apt-get install mpd
```
```
sudo apt-get install mpg123
```
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
Add folowing entries to crontab to execute this script on a regular time basis by running:
```
crontab -e
```
```
30 7,9,11,13,15,17,19,21,23 * * * python /home/pi/moje/python/pogoda/pogoda.py --typical >/dev/null 2>&1
00 8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24 * * * python /home/pi/moje/python/pogoda/pogoda.py --time >/dev/null 2>&1
```
You can trigger this script using IR remote.
##Author
Kamil Cyrkler
