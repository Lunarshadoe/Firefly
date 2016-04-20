# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-19 15:57:29
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-04-19 17:15:41
from astral import Astral
from astral import GoogleGeocoder
from datetime import datetime, timedelta
import json

from core.scheduler import Scheduler as ffScheduler
from core.models.command import Command as ffCommand
from core.models.event import Event as ffEvent

l_scheduler = ffScheduler()


class Location(object):
  def __init__(self, config_file):
    self._config_file = config_file
    self._modes = []
    self._a = None
    self._city = None
    self._zipcode = None
    self._isDark = True
    self._weather = None

    self._latitude = None
    self._longitude = None
    self.read_config_file()
    self.setup_local()

    self._mode = self._modes[0]
    self._last_mode = self._modes[0]
    
  @property
  def mode(self):
    return self._mode

  @property
  def last_mode(self):
    return self._last_mode

  @property
  def isDark(self):
    now = self.now()
    sun = self._city.sun(date=now, local=True)
    if now >= sun['sunset'] or now <= sun['sunrise']:
      return True
    return False

  @property
  def isLight(self):
    return not self.isDark

  @property
  def longitude(self):
      return self._longitude

  @property
  def latitude(self):
      return self._latitude
  
  
  
  @mode.setter
  def mode(self, value):
    value = str(value)
    if value in self._modes:
      self._last_mode = self._mode
      self._mode = value
      #ffNotify('all', 'LOCATION: Mode has changed to: ' + str(value))
      return True
    return False

  def read_config_file(self):
    with open(self._config_file) as data_file:
      config = json.load(data_file)
      self._zipcode = config.get('zip_code')
      self._modes = config.get('modes')

      print self._modes
      print self._zipcode

  def setup_local(self):
    self._a = Astral(GoogleGeocoder)
    self._a.solar_depression = 'civil'
    self._city = self._a[self._zipcode]
    self._latitude = self._city.latitude
    self._longitude = self._city.longitude

    #Prep Timers 
    dawn_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['dawn']
    now = self.now()
    if dawn_time < now:
      dawn_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dawn']
    print "Dawn Time: " + str(dawn_time)
    delay_s = (dawn_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.dawn_handler, replace=True, uuid='DawnScheduler')

    sunrise_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['sunrise']
    now = self.now()
    if sunrise_time < now:
      sunrise_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunrise']
    print "Sunrise Time: " + str(sunrise_time)
    delay_s = (sunrise_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunrise_handler, replace=True, uuid='SunriseScheduler')

    noon_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['noon']
    now = self.now()
    if noon_time < now:
      noon_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['noon']
    print "Noon Time: " + str(noon_time)
    delay_s = (noon_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.noon_handler, replace=True, uuid='NoonScheduler')

    sunset_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['sunset']
    now = self.now()
    if sunset_time < now:
      sunset_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunset']
    print "Sunset Time: " + str(sunset_time)
    delay_s = (sunset_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunset_handler, replace=True, uuid='SunsetScheduler')

    dusk_time = self._city.sun(date=datetime.now(self._city.tz), local=True)['dusk']
    now = self.now()
    if dusk_time < now:
      dusk_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dusk']
    print "Dusk Time: " + str(dusk_time)
    delay_s = (dusk_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.dusk_handler, replace=True, uuid='DuskScheduler')



  def dawn_handler(self):
    print 'Dawn Handler'
    #ffNotify('Zach Pushover', 'LOCATION: It is dawn!')

    now = self.now()
    dawn_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dawn']
    print "Dawn Time: " + str(dawn_time)
    delay_s = (dawn_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.dawn_handler, replace=True, uuid='DawnScheduler')

  def sunrise_handler(self):
    print 'Sunrise Handler'
    #ffNotify('Zach Pushover', 'LOCATION: It is sunrise!')

    now = self.now()
    sunrise_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunrise']
    print "Sunrise Time: " + str(sunrise_time)
    delay_s = (sunrise_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunrise_handler, replace=True, uuid='SunriseScheduler')

  def noon_handler(self):
    print 'Noon Handler'
    #ffNotify('Zach Pushover', 'LOCATION: It is noon!')

    now = self.now()
    noon_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['noon']
    print "Noon Time: " + str(noon_time)
    delay_s = (noon_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.noon_handler, replace=True, uuid='NoonScheduler')

  def sunset_handler(self):
    print 'Sunset Handler'
    #ffNotify('Zach Pushover', 'LOCATION: It is sunset!')

    now = self.now()
    sunset_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['sunset']
    print "Sunset Time: " + str(sunset_time)
    delay_s = (sunset_time - now).total_seconds()
    l_scheduler.runInS(delay_s, self.sunset_handler, replace=True, uuid='SunsetScheduler')

  def dusk_handler(self):
    print 'Dusk Handler'
    #ffNotify('Zach Pushover', 'LOCATION: It is dusk!')

    now = self.now()
    dusk_time = self._city.sun(date=datetime.now(self._city.tz) + timedelta(days=1), local=True)['dusk']
    print "Dusk Time: " + str(dusk_time)
    delay_s = (dusk_time - now).total_seconds()
    print 'Scheduling in ' + str(delay_s)
    l_scheduler.runInS(delay_s, self.dusk_handler, replace=True, uuid='DuskScheduler')

  def now(self):
    return datetime.now(self._city.tz)