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

import sqlite3
import os
from PIL import Image, ImageTk

script_path = os.path.split(os.path.abspath(__file__))[0]
db_file = F'{script_path}/stations.db'

# Tabelle stations
tab_stations = 'stations'
stations_struct = [
        {'col_name':'changeuuid',         'col_type':'text',    'col_key':''},   
        {'col_name':'stationuuid',        'col_type':'text',    'col_key':'primary key'},   
        {'col_name':'name',               'col_type':'text',    'col_key':''},   
        {'col_name':'url',                'col_type':'text',    'col_key':''},   
        {'col_name':'url_resolved',       'col_type':'text',    'col_key':''},   
        {'col_name':'homepage',           'col_type':'text',    'col_key':''},   
        {'col_name':'favicon',            'col_type':'text',    'col_key':''},   
        {'col_name':'tags',               'col_type':'text',    'col_key':''},   
        {'col_name':'country',            'col_type':'text',    'col_key':''},   
        {'col_name':'countrycode',        'col_type':'text',    'col_key':''},   
        {'col_name':'state',              'col_type':'text',    'col_key':''},   
        {'col_name':'language',           'col_type':'text',    'col_key':''},   
        {'col_name':'votes',              'col_type':'integer', 'col_key':''},   
        {'col_name':'lastchangetime',     'col_type':'text',    'col_key':''},   
        {'col_name':'codec',              'col_type':'text',    'col_key':''},   
        {'col_name':'bitrate',            'col_type':'integer', 'col_key':''},   
        {'col_name':'hls',                'col_type':'integer', 'col_key':''},   
        {'col_name':'lastcheckok',        'col_type':'integer', 'col_key':''},   
        {'col_name':'lastchecktime',      'col_type':'text',    'col_key':''},   
        {'col_name':'lastlocalchecktime', 'col_type':'text',    'col_key':''},   
        {'col_name':'clicktimestamp',     'col_type':'text',    'col_key':''},   
        {'col_name':'clickcount',         'col_type':'integer', 'col_key':''},   
        {'col_name':'clicktrend',         'col_type':'integer', 'col_key':''}   
    ]

# Tabelle favorites
tab_favorites = 'favorites'
favorites_struct = [
        {'col_name':'stationuuid',        'col_type':'text',    'col_key':'primary key'}
    ]

# maximale Anzahl der anzeigbaren Suchergebnisse
max_search_result_count = 2000


# ******************************************************************
def get_create_sql(struct, tab_name):
    s = f'create table if not exists {tab_name} ('
    comma = ''
    for l in struct:
        s=s+f"{comma} {l['col_name']} {l['col_type']} {l['col_key']}"
        comma = ','
    s = s +')'
    return s

# ******************************************************************
def get_insert_sql(struct, values, tab_name):
    s = f'insert or replace into {tab_name} values('
    comma = ''
    for l in struct:
        if isinstance(values[l['col_name']], str) == True:
            apos = "'"
        else:
            apos = ""
        s=s+f"{comma} {apos}{values[l['col_name']]}{apos}"
        comma = ','
    s = s +')'
    return s

# ******************************************************************
def sql_execute(sql):
    db=sqlite3.connect(db_file)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    result = cursor.execute(sql)
    l = []
    for row in result:
        l.append(row)
    db.commit()
    db.close()
    return l

# ******************************************************************
def get_station_count():
    c = sql_execute(f'select count(*) from {tab_stations}')
    return c[0][0]    

# ******************************************************************
def get_all_countrys():
    c = sql_execute(f'select country from {tab_stations} group by country order by country')
    l = []
    for row in c:
        l.append(row['country'])
    return l

# ******************************************************************
def get_all_countrycodes():
    c = sql_execute(f'select countrycode from {tab_stations} group by countrycode order by countrycode')
    l = []
    for row in c:
        l.append(row['countrycode'])
    return l

# ******************************************************************
def get_all_states():
    c = sql_execute(f'select state from {tab_stations} group by state order by state')
    l = []
    for row in c:
        l.append(row['state'])
    return l

# ******************************************************************
def get_filtered_stationnames(name, tags, country, countrycode, state, language):
    sql = f'select stationuuid, name from {tab_stations}'
    if name != '' or tags != '' or country != '' or countrycode != '' or state != '' or language != '':
        op = ''
        sql = f'{sql} where'
        if name != '':
            sql = f'{sql} {op} name like "%{name}%"'
            op = 'and'
        if tags != '':
            sql = f'{sql} {op} tags like "%{tags}%"'
            op = 'and'
        if country != '':
            sql = f'{sql} {op} country = "{country}"'
            op = 'and'
        if countrycode != '':
            sql = f'{sql} {op} countrycode = "{countrycode}"'
            op = 'and'
        if state != '':
            sql = f'{sql} {op} state = "{state}"'
            op = 'and'
        if language != '':
            sql = f'{sql} {op} language like "%{language}%"'
            op = 'and'
    
    c = sql_execute(sql)
    l = []
    for row in c:
        l.append(row)
    #print(len(l))
    return l    
    
# ******************************************************************
def get_stationinfo(stationuuid):
    c = sql_execute(f'select * from {tab_stations} where stationuuid = "{stationuuid}"')
    return c    

# ******************************************************************
def get_all_favorites():
    sql = f"select stationuuid, name from {tab_stations} where stationuuid in (select stationuuid from {tab_favorites}) order by name"
    c = sql_execute(sql)
    l = []
    for row in c:
        l.append(row)
    return l    

# ******************************************************************
def delete_favorite(stationuuid):
    c = sql_execute(f'delete from {tab_favorites} where stationuuid = "{stationuuid}"')
    return c    

# ******************************************************************
def get_icon(f, dx, dy):
    icon = Image.open(f)
    icon = icon.resize((dx, dy), Image.ANTIALIAS)
    icon = ImageTk.PhotoImage(icon)
    return icon
