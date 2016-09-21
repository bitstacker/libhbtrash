

import os
import urllib.parse
import re
import urllib.request
import json
from bs4 import BeautifulSoup
from datetime import datetime,timedelta,date
from icalendar import Calendar, Event, vDate, Alarm

class Muell(object):
    typ = 0
    def __init__(self, typ):
        self.typ = typ
    def __str__(self):
        if self.typ == 1:
            return "Restmüll / Biotonne"
        elif self.typ == 2:
            return "Papier / Gelber Sack"
        elif self.typ == 3:
            return "Tannenbaumabfuhr"
        else:
            return "Unbekannt"
    def __int__(self):
        return int(self.typ)
    
    
class Muellplan(object):
    SERVERPATH="http://213.168.213.236/bremereb/bify/bify.jsp"

    def getIcal(self,street='',number='',addition='',alarm=''):
        bify = self.__fetchBifyForStreetAndNumber(street,number,addition)
        eventlist = self.__findTrashEventsInContent(bify)
        ical = self.__getiCalFromEventlist(eventlist,alarm)
        return ical

    def __fetchBifyForStreetAndNumber(self,street,number,addition=''):
        street = urllib.parse.quote(street,encoding="ISO-8859-1")
        number = urllib.parse.quote(number,encoding="ISO-8859-1")
        if addition != '':
            addition = urllib.parse.quote(addition,encoding="ISO-8859-1")
            url = self.SERVERPATH + "?strasse={}&hausnummer={}&zusatz={}".format(street,number,addition)
        else:
            url = self.SERVERPATH + "?strasse={}&hausnummer={}".format(street,number)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            content = response.read()
        content = content.decode("ISO-8859-1")
        content = content.replace("<nobr><br>","</nobr>")#Hack for parsing siblings
        return content

    def __findTrashEventsInContent(self,content):
        soup = BeautifulSoup(content, "lxml")
        eventlist = []
        
        for month in soup.find_all("b",text=re.compile("^\w+\s\d{4}")):
            current_year = self.__getYearFromMonthString(month.string)
            for sibling in month.find_next_siblings("nobr",text=re.compile("^(\(\w{2}\)\s)?\d{2}\.\d{2}\.\s")):
                current_date = self.__getDateObjectFromEventString(current_year,sibling.string)
                trashtype = self.__getTrashTypeFromEventString(sibling.string)
                eventlist.append([current_date,trashtype])
        return eventlist
    
    def __getYearFromMonthString(self, month_s):
        year = month_s.split(" ")[1]
        return year

    def __getDateObjectFromEventString(self, current_year, date_s):
        date_s = self.__cutDayNoticeWhenNeeded(date_s)
        complete_string = date_s.split()[0] + current_year
        the_datetime = datetime.strptime(complete_string,"%d.%m.%Y")
        the_date = date(the_datetime.year,the_datetime.month,the_datetime.day)
        return the_date

    def __cutDayNoticeWhenNeeded(self,date_s):
        matcher = re.compile("^\(\w{2}\)\s") # For (Sa),(Fr) etc.
        if matcher.match(date_s):
            date_s = date_s[5:]
        return date_s

    def __getTrashTypeFromEventString(self, event_s):
        event_s = self.__cutDayNoticeWhenNeeded(event_s)
        trash_string = event_s[7:]
        if trash_string in ["Restmüll / Bioabfall","Restm. / Bioabf."]:
            trashtype = Muell(1)
        elif trash_string in ["Papier / Gelber Sack","Papier / G.Sack"]:
            trashtype = Muell(2)
        elif trash_string == "Tannenbaumabfuhr":
            trashtype = Muell(3)
        else:
            trashtype = Muell(0)
        return trashtype

    def __getiCalFromEventlist(self, eventlist, alarm):
        cal = Calendar()
        cal.add('prodid', 'libhbtrash')
        cal.add('version', '0.1')
        for event in eventlist:
            icalevent = Event()
            icalevent.add('dtstart', event[0])
            icalevent.add('dtend', event[0] + timedelta(days=1))
            icalevent.add('summary', str(event[1]))
            if alarm != '':
                alarmtime = timedelta(minutes=-int(alarm))
                icalalarm = Alarm()
                icalalarm.add('action','DISPLAY')
                icalalarm.add('trigger',alarmtime)
                icalevent.add_component(icalalarm)
            cal.add_component(icalevent)
        cal = cal.to_ical()
        cal = cal.decode("utf-8")
        return cal
    def getNextDateJson(self, street, number, addition):
        bify = self.__fetchBifyForStreetAndNumber(street,number,addition)
        eventlist = self.__findTrashEventsInContent(bify)
        now = date.today()
        nowlong = datetime.today().strftime("%d.%m.%Y %H:%M:%S")
        nextevent = ""
        for event in eventlist:
            if event[0] >= now:
                nextevent = event
                break
        data = {
                'date': nextevent[0].strftime("%d.%m.%Y"),
                'type': int(nextevent[1]),
                'lastupdate': nowlong
                }
        return json.dumps(data)

