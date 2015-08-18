# -*- coding: utf-8 -*-

# Talking Weather ver. 0.01
# Author : Kamil Cyrkler
# Date : 21/09/2014

# wymaga odtwarzacza mpg123

import urllib2 , json, subprocess, sys, textwrap, datetime, time, re, os

greeting = ' pora na informacje dnia' #powitanie
pre_event = 'Uwaga komunikat: '# przedmowa przed zdarzeniem dnia
fragmentation_factor = 100; #co ile znaków dzielić tekst (domyślnie 100 dla google tts)
mpd_playing=False #zmienna globalna do przerywania odtwarzanej myzyki przez serwer MPD na czas trwania komunikatu - nie zmieniac!
json_forecast = 'http://api.wunderground.com/api/b2b4a1ad0a889006/forecast/conditions/lang:PL/q/Poland/Lublin.json' #sciezka dostępu do pliku json z pogodą
imieniny_path = '/home/pi/moje/python/pogoda/data/imieniny.txt'#sciezka do pliku z imieninami
event_path = '/home/pi/moje/python/pogoda/data/events.txt' #sciezka do pliku ze zdarzeniami (ważne daty. np urodziny członków rodziny itd)
beep_1_path = '/home/pi/moje/python/pogoda/sounds/news_intro.mp3'
beep_2_path = '/home/pi/moje/python/pogoda/sounds/kogut.mp3'
beep_3_path = '/home/pi/moje/python/pogoda/sounds/chime3.mp3'
beep_4_path = '/home/pi/moje/python/pogoda/sounds/bloop.mp3'
replace_words = {'temp.':'temperatura', 'Min.':'minimalna', 'pd.':' południowo', 'pn.':' połnocno', 'zach.':' zachodni', 'wsch.':' wschodni', 'op.':' opady', 'Maks.':'maksymalna', '~':''}

#funkcja do dzielenia tekstu na kawalki
def split_by_n( seq, n ): 
    while seq:
		
        yield seq[:n]
        seq = seq[n:]
#funkcja do wypowiadania tekstu
def say(output_text,delay):
	output_text_fragmented = textwrap.wrap(output_text, fragmentation_factor)
	for i in output_text_fragmented:
		print('OUT: '+i)
		subprocess.call(['mpg123 -q "http://translate.google.com/translate_tts?tl=pl&q='+i+'&ie=UTF-8&total=1&idx=0&client=t"'], shell=True)
		time.sleep(delay)

#funkcja do zamiany tekstu
def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


#funkcja głowna broadcast nadaje komunikaty clist-lista tekstow delay-opoznienie w sekundach przy wymienianiu kolejnych tekstow def=1
def broadcast(clist,delay):
	mpd_check_before()
	if clist==broadcast_text_typical:
		subprocess.call('mpg123 -q '+beep_1_path, shell=True) #odtworz beep przed rozpoczeciem komunikatu
		for i in clist:
			say(i,delay)
		subprocess.call('mpg123 -q '+beep_1_path, shell=True) #odtworz beep po zakonczeniu komunikatu
	elif clist==broadcast_text_time:
		subprocess.call('mpg123 -q '+beep_3_path, shell=True) #odtworz beep przed rozpoczeciem komunikatu
		for i in clist:
			say(i,delay)
	elif clist==broadcast_text_typical_event:
		subprocess.call('mpg123 -q '+beep_2_path, shell=True) #odtworz beep przed rozpoczeciem komunikatu
		for i in clist:
			say(i,delay)
		subprocess.call('mpg123 -q '+beep_2_path, shell=True) #odtworz beep po zakonczeniu komunikatu
	else:
		subprocess.call('mpg123 -q '+beep_4_path, shell=True) #odtworz beep przed rozpoczeciem komunikatu
		for i in clist:
			say(i,delay)
		subprocess.call('mpg123 -q '+beep_4_path, shell=True) #odtworz beep po zakonczeniu komunikatu
	mpd_check_after()
#funkcja wyciaga ilość (amount) pierwszych zdań z parametru (text) oddzielonych .:; itd
def extract_sentences(text,amount):

	text=(' '.join(re.split(r'(?<=[.:;])\s', text)[:amount]))
	
	return text
		
#funkcja sprawdza czy dzisiaj nie ma zdarzenia zdefiniowanego w pliku events.txt		
def event_today(path):
	now = datetime.datetime.now()
	if len(str(now.month))<2:
		month_l='0'+str(now.month)
	else:
		month_l=str(now.month)
	if len(str(now.day))<2:
		day_l='0'+str(now.day)
	else:
		day_l=str(now.day)
	try:
		event_list = open(path).read().splitlines()
		for i in event_list:
			if (i[0:2]==day_l and i[3:5]==month_l):
				output = i[6:]
				return output
				break
	except IOError:
		return 'Błąd. Nie znaleziono pliku bazy imienin (imieniny.txt).' 

def jest_godzina():
	return time.strftime("%H:%M")
	
f = urllib2.urlopen(json_forecast) 
json_string = f.read() 
parsed_json = json.loads(json_string) 
f.close()

#funkcje przerywaja odtwarzana muzyke przez serwer MPD na czas trwania komunikatu
def mpd_check_before():
	global mpd_playing
	f=os.popen("mpc -f %name% current").read()
	if len(f)==0: #przypadek kiedy nie jest odtwarzana muzyka
		mpd_playing = False
	else:			#przypadek kiedy jest odtwarzana muzyka
		mpd_playing = True
		os.popen("mpc pause")
		time.sleep(1)
		
def mpd_check_after():
	global mpd_playing
	if mpd_playing==True:
		time.sleep(1)
		os.popen("mpc toggle")

#zmienne danych pogodowych :
cur_weekday = parsed_json['forecast']['simpleforecast']['forecastday'][0]['date']['weekday'].encode("utf8") #nazwa dnia tygodnia np. 'Poniedziałek'
cur_day = str(parsed_json['forecast']['simpleforecast']['forecastday'][0]['date']['day']).encode("utf8") #dzień
cur_month = parsed_json['forecast']['simpleforecast']['forecastday'][0]['date']['monthname'].encode("utf8") #nazwa miesiaca polska np. 'wrzesień'
cur_year = str(parsed_json['forecast']['simpleforecast']['forecastday'][0]['date']['year']).encode("utf8") #rok
pop = parsed_json['forecast']['txt_forecast']['forecastday'][0]['pop'].encode("utf8") #prawdopodobienstwo opadow

feelslike_c = str(parsed_json['current_observation']['feelslike_c']).encode("utf8") #odczuwalna temp w st. C
wind_gust_kph = str(parsed_json ['current_observation']['wind_gust_kph']).encode("utf8") #predkosc wiatru w porywach w km/h
pressure_mb = str(parsed_json['current_observation']['pressure_mb']).encode("utf8") #cisnienie atmosferyczne w hPa

current_conditions = parsed_json['forecast']['txt_forecast']['forecastday'][0]['fcttext_metric'].encode("utf8")
current_conditions = replace_all(current_conditions,replace_words) #zamiana slow np. ('min.' -> 'minimalna')
current_conditions = extract_sentences(current_conditions,2)	#wybierz 2 pierwsze zdania

tommorow_conditions = parsed_json['forecast']['txt_forecast']['forecastday'][2]['fcttext_metric'].encode("utf8")
tommorow_conditions = replace_all(tommorow_conditions,replace_words) #zamiana slow np. ('min.' -> 'minimalna')
tommorow_conditions = extract_sentences(tommorow_conditions,2)	#wybierz 2 pierwsze zdania

#struktura różnych komunikatów

#komunikat standardowy
broadcast_text_typical = [
	'Godzina '+jest_godzina()+'. Pora na informacje dnia:',
	'Dzisiaj jest '+cur_weekday+' '+cur_day+'-'+cur_month+'-'+cur_year,
	'Imieniny: '+event_today(imieniny_path),
	#'Słowo jabłko w języku angielskim brzmi: apple', do opracowania w przyszlosci losowe slowka w losowych jezykach
	'Odczuwalna temperatura na dworze to '+feelslike_c+' °C',
	current_conditions, 
	'Ciśnienie atmosferyczne wynosi '+pressure_mb+' hPa',
	'Wiatr w porywach z prędkością do '+wind_gust_kph+' km/h',
	'Jutro natomiast '+tommorow_conditions #JSON.forecast.txt_forecast.forecastday[2].fcttext_metric
	] 
	
#komunikat ze zdarzeniem z events.txt	
broadcast_text_typical_event = [
	'Godzina '+jest_godzina()+'. Uwaga specjalny komunikat:',
	event_today(event_path),
	'Koniec specjalnego komunikatu.',
	'Dzisiaj jest '+cur_weekday+' '+cur_day+'-'+cur_month+'-'+cur_year,
	'Imieniny: '+event_today(imieniny_path),
	#'Słowo jabłko w języku angielskim brzmi: apple', do opracowania w przyszlosci losowe slowka w losowych jezykach
	'Odczuwalna temperatura na dworze to '+feelslike_c+' °C',
	current_conditions, 
	'Ciśnienie atmosferyczne wynosi '+pressure_mb+' hPa',
	'Wiatr w porywach z prędkością do '+wind_gust_kph+' km/h',
	'Jutro natomiast '+tommorow_conditions #JSON.forecast.txt_forecast.forecastday[2].fcttext_metric
]

#komunikat czasu
broadcast_text_time = [
	'Wybiła godzina '+jest_godzina(),
	]



		
#obsluga z argumentami np. pogoda.py --time (podaje czas)

if len(sys.argv) < 2: #blad gdy nie podano parametru
    sys.exit('Błąd [E01] - Nie podano parametru. \n Spróbuj: \n python pogoda.py --typical (podaje informacje o aktualnej pogodzie)\n python pogoda.py --time (podaje aktualną godzinę)')
#obsluga parametrow
if not os.path.exists(sys.argv[1]):
	if sys.argv[1]=='--typical':
		if event_today(event_path) is None: 
			broadcast(broadcast_text_typical,1) #zwykly komunikat
		else:
			broadcast(broadcast_text_typical_event,1) #specjalny komunikat ze zdarzeniem
	elif sys.argv[1]=='--time':
		broadcast(broadcast_text_time,1)
	else:
		sys.exit('Błąd [E02] - Niepoprawny parametr. \n Spróbuj: \n python pogoda.py --typical (podaje informacje o aktualnej pogodzie)\n python pogoda.py --time (podaje aktualną godzinę)')
	sys.exit('END.')

