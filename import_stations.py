#!/usr/bin/env python3
#
# ******************************************************************************************************************
#
#    Import Liste Internetradiostationen in eine SQLite-DB
#    =====================================================
#                   Uwe Berger, 2021
#
#    Datenquelle:
#    https://www.radio-browser.info/#!/
#
#    API:
#    https://de1.api.radio-browser.info/
#
#    Datenstrukur:
#    {
#    "changeuuid":"960e57c8-0601-11e8-ae97-52543be04c81",
#    "stationuuid":"960e57c5-0601-11e8-ae97-52543be04c81",
#    "name":"SRF 1",
#    "url":"http://stream.srg-ssr.ch/m/drs1/mp3_128",
#    "url_resolved":"http://stream.srg-ssr.ch/m/drs1/mp3_128",
#    "homepage":"http://ww.srf.ch/radio-srf-1",
#    "favicon":"https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Radio_SRF_1.svg/205px-Radio_SRF_1.svg.png",
#    "tags":"srg ssr,public radio",
#    "country":"Switzerland",
#    "countrycode":"CH",
#    "state":"",
#    "language":"german",
#    "votes":0,
#    "lastchangetime":"2019-12-12 18:37:02",
#    "codec":"MP3",
#    "bitrate":128,
#    "hls":0,
#    "lastcheckok":1,
#    "lastchecktime":"2020-01-09 18:16:35",
#    "lastcheckoktime":"2020-01-09 18:16:35",
#    "lastlocalchecktime":"2020-01-08 23:18:38",
#    "clicktimestamp":"",
#    "clickcount":0,
#    "clicktrend":0
#    }
#
#    ---------
#    Have fun!
#
# *******************************************************************************************************************

from pyradios import RadioBrowser
import my_func
import sqlite3


# ******************************************************************
def convert_str(s):
  s=s.replace("'","")
  s=s.replace('\x00','')
  return s

# ******************************************************************
# ******************************************************************
# ******************************************************************
db=sqlite3.connect(my_func.db_file)
cur = db.cursor()

print('Daten holen.')
rb=RadioBrowser()

#x=rb.search(name='BBC Radio 1', name_exact=True)
x=rb.search()

print(len(x), 'Datensätze empfangen')

print('Tabelle', my_func.tab_stations, 'anlegen.')
sql = my_func.get_create_sql(my_func.stations_struct, my_func.tab_stations)
cur.execute(sql)

old_count = my_func.get_station_count()
print(old_count, ' Datensätze aktuell in DB')

print('Datensätze in Tabelle', my_func.tab_stations, 'einfügen')
count=0
for e in x:
  for key in e.keys():
    if isinstance(e[key], str) == True:
      e[key]=convert_str(e[key])
    sql = my_func.get_insert_sql(my_func.stations_struct, e, my_func.tab_stations)
  try:
    cur.execute(sql)
  except sqlite3.Error as er:
    print(er)
  count=count+1
  if (count%1000)==0:
    db.commit()
    print(count, ' Datensätze verarbeitet...')
db.commit()

print(count, ' Datensätze insgesamt...')
new_count = my_func.get_station_count()
insert_count = new_count - old_count
replace_count = count - insert_count
print(insert_count, ' Inserts')
print(replace_count, ' Replaces')

db.close()
exit()

