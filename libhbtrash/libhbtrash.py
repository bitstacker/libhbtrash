#/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib.parse
import re
import urllib.request
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
    
    
class Muellplan(object):
    SERVERPATH="http://213.168.213.236/bremereb/bify/bify.jsp"

    def __init__(self,street='',number='',addition='',alarm=''):
        ical = self.getIcal(street,number,addition,alarm)
        print(ical)        

    def getIcal(self,street='',number='',addition='',alarm=''):
        bify = self.fetchBifyForStreetAndNumber(street,number,addition)
        eventlist = self.findTrashEventsInContent(bify)
        ical = self.getiCalFromEventlist(eventlist,alarm)
        return ical

    def fetchBifyForStreetAndNumber(self,street,number,addition=''):
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

    def findTrashEventsInContent(self,content):
        soup = BeautifulSoup(content, "lxml")
        eventlist = []
        
        for month in soup.find_all("b",text=re.compile("^\w+\s\d{4}")):
            current_year = self.getYearFromMonthString(month.string)
            for sibling in month.find_next_siblings("nobr",text=re.compile("^(\(\w{2}\)\s)?\d{2}\.\d{2}\.\s")):
                current_date = self.getDateObjectFromEventString(current_year,sibling.string)
                trashtype = self.getTrashTypeFromEventString(sibling.string)
                eventlist.append([current_date,str(trashtype)])
        return eventlist
    
    def getYearFromMonthString(self, month_s):
        year = month_s.split(" ")[1]
        return year

    def getDateObjectFromEventString(self, current_year, date_s):
        date_s = self.cutDayNoticeWhenNeeded(date_s)
        complete_string = date_s.split()[0] + current_year
        the_datetime = datetime.strptime(complete_string,"%d.%m.%Y")
        the_date = date(the_datetime.year,the_datetime.month,the_datetime.day)
        return the_date

    def cutDayNoticeWhenNeeded(self,date_s):
        matcher = re.compile("^\(\w{2}\)\s") # For (Sa),(Fr) etc.
        if matcher.match(date_s):
            date_s = date_s[5:]
        return date_s

    def getTrashTypeFromEventString(self, event_s):
        event_s = self.cutDayNoticeWhenNeeded(event_s)
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

    def getiCalFromEventlist(self, eventlist, alarm):
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


