#!/usr/bin/python3

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

# own files
import send_mail
import plotting_graph
import login

# own2
import sqlite3
import time
import datetime

def getForecastXMLFromAPI():
  try:
    response = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q=Stuttgart,de&mode=xml&appid=' + login.appid)
  except urllib.error.HTTPError as err:
    if err.code == 404:
      return "error 404"
    elif err.code == 403:
      return "error 403"
    else:
      r =  "error! Error code", err.code
      return r
  except urllib.error.URLError as err:
    r = "error happened:", err.reason
    return r
  
  xml2 = response.read()
  response.close()
  return xml2


def getWeatherXMLFromAPI():
  try:
    response = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=Stuttgart,de&mode=xml&appid=' + login.appid)
  except urllib.error.HTTPError as err:
    if err.code == 404:
      return "error 404"
    elif err.code == 403:
      return "error 403"
    else:
      r =  "error! Error code", err.code
      return r
  except urllib.error.URLError as err:
    r = "error happened:", err.reason
    return r
    
  xml2 = response.read()
  response.close()
  return xml2


def connectToDatabase():
  conn = sqlite3.connect('weather.db')
  # conn.execute('''DROP TABLE WEATHERDATA;''')
  conn.execute('''CREATE TABLE IF NOT EXISTS WEATHERDATA
       (
        TIMEOFVALUES      TIMESTAMP  UNIQUE   NOT NULL,
        TEMPMIN           TEXT     NOT NULL,
        TEMPMAX           TEXT     NOT NULL,
        TEMPVALUE         TEXT     NOT NULL,
        TEMPREAL          TEXT     NULL,
        NAME              TEXT     NOT NULL,
        PREVALUE          TEXT     NOT NULL,
        PRETYPE           TEXT     NOT NULL,
        PREREAL           TEXT     NULL,
        WINDSPEED         TEXT     NOT NULL,
        WINDNAME          TEXT     NOT NULL,
        WINDREAL          TEXT     NULL,
        PRESSUREVALUE     TEXT     NOT NULL,
        PRESSUREREAL      TEXT     NULL,
        HUMVALUE          TEXT     NOT NULL,
        HUMREAL           TEXT     NULL,
        CLOUDVALUE        TEXT     NOT NULL,
        CLOUDALL          TEXT     NOT NULL,
        CLOUDREAL         TEXT     NULL
       );''')
  conn.execute('''CREATE TABLE IF NOT EXISTS SUNDATA
       (
        SUNRISE     TEXT    NOT NULL,
        SUNSET      TEXT    NOT NULL,
        OFDATE      DATE    UNIQUE     NOT NULL,
        SUNRISEREAL TEXT    NULL,
        SUNSETREAL  TEXT    NULL
       );''')
  return conn


def closeDatabase( conn ):
  conn.close()


def insertSunData( root , conn ):
  for sun in root.findall('sun'):
    rise = sun.get('rise')
    sunset = sun.get('set')
    sqlQuery = 'REPLACE INTO SUNDATA (SUNRISE, SUNSET, OFDATE) VALUES ( \''+rise+'\' , \''+sunset+'\' , date(\'now\') )'
    conn.execute( sqlQuery )


def insertForecastData( root , conn ):
  for forecast in root.findall('forecast'):
    for times in forecast.findall('time'):
      t = time.mktime(time.strptime(times.get('from'), "%Y-%m-%dT%H:%M:%S"))
#      t = time.get('from')
      sqlQuery = 'REPLACE INTO WEATHERDATA ( TIMEOFVALUES , TEMPREAL , PREREAL , WINDREAL , PRESSUREREAL , HUMREAL , CLOUDREAL , TEMPMIN , TEMPMAX , TEMPVALUE , NAME , PREVALUE , PRETYPE , WINDSPEED , WINDNAME , PRESSUREVALUE , HUMVALUE , CLOUDVALUE , CLOUDALL ) VALUES ( '+ str(t) +' , 0 , 0 , 0 , 0 , 0 , 0 ,'
      for temperature in times.findall('temperature'):
        if(temperature.get('unit') == 'kelvin'):
          tempvalue = float(temperature.get('value'))-273.15
          tempmin = float(temperature.get('min'))-273.15
          tempmax = float(temperature.get('max'))-273.15
        else:
          tempvalue = float(temperature.get('value'))
          tempmin = float(temperature.get('min'))
          tempmax = float(temperature.get('max'))
        sqlQuery += '\''+ str(tempmin) +'\' , \''+ str(tempmax) + '\' , \''+ str(tempvalue) + '\' , '
      for symbol in times.findall('symbol'):
        namevalue = symbol.get('name')
        sqlQuery += '\''+ namevalue +'\' , '
      for preci in times.findall('precipitation'):
        if preci.get('value'):
          prevalue = preci.get('value')
        else:
          prevalue = 'NULL'
        if preci.get('type'):
          pretype = preci.get('type')
        else:
          pretype = 'NULL'
        sqlQuery += '\''+ prevalue +'\' , \''+ pretype +'\' , '
      for wind in times.findall('windSpeed'):
        windspeed = wind.get('mps')
        windname = wind.get('name')
        sqlQuery += '\''+ windspeed +'\' , \''+ windname +'\' , '
      for press in times.findall('pressure'):
        pressvalue = press.get('value')
        sqlQuery += '\''+ pressvalue +'\' , '
      for hum in times.findall('humidity'):
        humvalue = hum.get('value')
        sqlQuery += '\''+ humvalue +'\' , '
      for cloud in times.findall('clouds'):
        cloudvalue = cloud.get('value')
        cloudall = cloud.get('all')
        sqlQuery += '\''+ cloudvalue +'\' , \''+ cloudall +'\' );'
      conn.execute( sqlQuery )
      # print(sqlQuery
  conn.commit()


def updateSunData( root , conn ):
  for city in root.findall('city'):
    for sun in city.findall('sun'):
      sunrise = sun.get('rise')
      sunset = sun.get('set')
      sqlQuery = 'UPDATE SUNDATA SET SUNRISEREAL = \''+ sunrise +'\' , SUNSETREAL = \''+ sunset +'\' WHERE OFDATE = Date(\'now\');'
  conn.execute( sqlQuery )
  conn.commit()


def updateForecastData( root , conn ):
  sqlQuery = 'UPDATE WEATHERDATA SET '
  for temperature in root.findall('temperature'):
    if(temperature.get('unit') == 'kelvin'):
      tempvalue = float(temperature.get('value'))-273.15
    else:
      tempvalue = float(temperature.get('value'))
    sqlQuery += 'TEMPREAL = \''+ str(tempvalue) +'\' , '
  for preci in root.findall('precipitation'):
    if( not preci.get('mode') == "no" ):
      sqlQuery += 'PREREAL = \''+ preci.get('value') +'\' , '
  for wind in root.findall('wind'):
    for speed in wind.findall('speed'):
      speedvalue = speed.get('value')
      sqlQuery += 'WINDREAL = \''+ speedvalue +'\' , '
  for press in root.findall('pressure'):
    pressvalue = press.get('value')
    sqlQuery += 'PRESSUREREAL = \''+ pressvalue +'\' , '
  for hum in root.findall('humidity'):
    humvalue = hum.get('value')
    sqlQuery += 'HUMREAL = \''+ humvalue +'\' , '
  for clouds in root.findall('clouds'):
    cloudvalue = clouds.get('value')
    sqlQuery += 'CLOUDREAL = \''+ cloudvalue +'\' '
  for lastupdate in root.findall('lastupdate'):
    lasttime = time.mktime(time.strptime(lastupdate.get('value'), "%Y-%m-%dT%H:%M:%S"))
    sqlQuery += 'WHERE TIMEOFVALUES BETWEEN '+ str(lasttime-5340) +' AND '+str(lasttime+5340) +';'
  conn.execute( sqlQuery )
  conn.commit()


def getTempArrayForPlot( conn ):
  cursor = conn.execute('SELECT TIMEOFVALUES , TEMPVALUE FROM WEATHERDATA;')
  ground = []
  for rows in cursor:
    t = datetime.datetime.fromtimestamp(int(rows[0])).strftime('%Y-%m-%d %H:%M:%S')
    if "12:" in t:
      ground.append(rows[1])
  return ground


def getHumArrayForPlot( conn ):
  cursor = conn.execute('SELECT TIMEOFVALUES , HUMVALUE FROM WEATHERDATA;')
  ground = []
  for rows in cursor:
    t = datetime.datetime.fromtimestamp(int(rows[0])).strftime('%Y-%m-%d %H:%M:%S')
    if "12:" in t:
      ground.append(rows[1])
  return ground


conn = connectToDatabase()
xmlForecast = getForecastXMLFromAPI()
if( not xmlForecast.startswith( b'error' )):
  root = ET.fromstring(xmlForecast)
  insertSunData( root , conn )
  insertForecastData( root , conn )
else:
  # ToDo SendMail with ErrorCode or write in Database
  print('Error')

xmlNow = getWeatherXMLFromAPI()
if( not xmlNow.startswith( b'error' )):
  root = ET.fromstring(xmlNow)
  updateSunData( root , conn )
  updateForecastData( root , conn )
else:
  # ToDo SendMail with ErrorCode or write in Database
  print('Error')


#cursor = conn.execute('SELECT strftime(\'%Y-%m-%d %H:%M:%S\',TIMEOFVALUES) , TEMPMIN , TEMPMAX , TEMPVALUE , TEMPREAL , NAME , PREVALUE , PRETYPE , PREREAL , WINDSPEED , WINDNAME , WINDREAL , PRESSUREVALUE , PRESSUREREAL , HUMVALUE , HUMREAL , CLOUDVALUE , CLOUDALL , CLOUDREAL FROM WEATHERDATA;')
# for row in cursor:
#   print "------------------------------------------------------"
#   print "TIMEOFVALUES= "+str(row[0])
#   print "TEMPMIN= "+str(row[1])
#   print "TEMPMAX= "+str(row[2])
#   print "TEMPVALUE= "+str(row[3])
#   print "TEMPREAL= "+str(row[4])
#   print "NAME= "+str(row[5])
#   print "PREVALU= "+str(row[6])
#   print "PRETYPE= "+str(row[7])
#   print "PREREAL= "+str(row[8])
#   print "WINDSPEED= "+str(row[9])
#   print "WINDNAME= "+str(row[10])
#   print "WINDREAL= "+str(row[11])
#   print "PRESSUREVALUE= "+str(row[12])
#   print "PRESSUREREAL= "+str(row[13])
#   print "HUMVALUE= "+str(row[14])
#   print "HUMREAL= "+str(row[15])
#   print "CLOUDVALUE= "+str(row[16])
#   print "CLOUDALL= "+str(row[17])
#   print "CLOUDREAL= "+str(row[18])

temp = getTempArrayForPlot( conn )
hum  = getHumArrayForPlot( conn )

closeDatabase( conn )

# Formatting Mail
mail_receiver = login.receiver
mail_sender = login.sender

text = """
<html>
    <head>
        <h1>Here is your forecast!</h1>
    </head>
    <body>
        <p><img src="cid:image1"></br>
        </br>
        Have a beautiful day!</br>
        </p>
    </body>
</html>
"""

# Plotting and attaching
plotting_graph.plot(temp,hum)
attach = 'plot.png'

#send_mail.send(mail_sender, mail_receiver, text, attach)
