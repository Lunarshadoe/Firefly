# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 23:50:08
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-12 23:05:30

import json
import logging
import requests #TODO: Replace with core.http_request

from core.models.event import Event as ffEvent

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

metadata = {
  'module' : 'ffHue_bridge'
}

class Bridge(object):
  '''
  Hue Bridge

  This is the core of zPyHue. There should only need to be one
  bridge object. The bridge object manages all the other objects
  and is able to look them up as needed. It also loads the config
  file and settigns.
  '''

  def __init__(self, deviceID, username=None, ip=None):
    self._id = deviceID
    self._ip = ip
    self._username = username
    self._name = None
    self._rCount = 0
    self._lights = []
    self._groups = []

    self._commands = {
      'sendLightRequest' : self.sendLightRequest,
      'sendGroupRequest' : self.sendGroupRequest
    }

    if not self._ip:
      self.get_ip()
    if not self._username:
      self.register()

    logging.debug('Hue Bridge IP: ' + str(self._ip))



  def sendEvent(self, event):
    logging.debug('Reciving Event in ' + str(metadata.get('module')) + ' ' + str(event))
    ''' NEED TO DECIDE WHAT TO DO HERE
    if event.deviceID == self._id:
      for item, value in event.event.iteritems():
        if item in self._commands: 
          self._commands[item](value)
    self.refreshData()
    '''

  def sendCommand(self, command):
    simpleCommand = None
    logging.debug('Reciving Command in ' + str(metadata.get('module')) + ' ' + str(command))
    if command.deviceID == self._id:
      for item, value in command.command.iteritems():
        if item in self._commands:
          simpleCommand = self._commands[item](value)
    
      ## OPTIONAL - SEND EVENT
      #if command.simple:
      #  ffEvent(command.deviceID, simpleCommand)
      #else:
      #  ffEvent(command.deviceID, command.command)
      ## OPTIONAL - SEND EVENT

  def requestData(self, request):
    logging.debug('Request made to ffPushover ' + str(request))
    if request.multi:
      returnData = {}
      for item in request.request:
        returnData[item] = self._requests[item]()
      return returnData

    elif not request.multi and not request.all:
      return self._requests[request.request]()

    elif request.all:
      pass
      #returnData = self.refreshData()
      #return returnData

####################################################################3

  def sendLightRequest(self, request):
    if 'lightID' in request.keys():
      logging.debug('Sending Light Request')
      self.send_request('lights/' + str(request.get('lightID')) + '/state', data=request.get('data'), method='PUT')


  def sendGroupRequest(self, request):
    if 'groupID' in request.keys():
      logging.debug('Sending Group Request')
      self.send_request('groups/' + str(request.get('groupID')) + '/action', data=request.get('data'), method='PUT')


  def send_request(self, path, data=None, method='GET', return_json=True, no_username=False):
    if data:
      data = json.dumps(data)

      logging.debug('Data: ' + data)

    url = ''
    if (no_username or not self._username):
      url = 'http://' + str(self._ip) + '/' + path
    else:
      url = 'http://' + str(self._ip) + '/api/' + self._username + '/' + path

    logging.debug('Request URL: ' + url + ' Method: ' + method)

    if method == 'POST':
      #r = requests.post(url, data=data)
      #if return_json:
      #  return r.json()
      #return r
      
      requests.post(url,data=data)

    elif method == 'PUT':
      requests.put(url,data=data)
      
      #r = requests.put(url, data=data)
      #if return_json:
      #  return r.json()
      #return r

    elif method == 'GET':
      if data:
        r = requests.get(url, data=data)
      else: 
        r = requests.get(url)
      if return_json:
        return r.json()
      return r


  def get_ip(self):
    data = requests.get('http://www.meethue.com/api/nupnp')
    try:
      self._ip = data.json()[0]['internalipaddress']
    except:
      logging.error('Problem parsing IP Address of Bridge')
      exit()
    if not self._ip:
      logging.error('Problem parsing IP Address of Bridge')
      exit()

    logging.debug('IP address: ' + str(self._ip))

  def register(self):
    request_data = {'devicetype':'zPyHue'}
    response = self.send_request('api', request_data, method='POST', no_username=True)[0]
    
    logging.debug('Response: ' + str(response))

    if 'error' in response:
      if response['error']['type'] == 101:
        logging.debug('Please press the hue button.')
        sleep(3)
        if (self._rCount < 30): 
          self.register()
        else:
          raise HueButtonNotPressed("Hue button was not pressed in the last 60 seconds")

    if 'success' in response:
      self._username = response['success']['username']
      logging.debug('Success! username: ' + str(self._username))

  def get_all(self):
    '''Returns all from /api/username'''
    return self.send_request('api/' + str(self._username), no_username=True)

  def get_lights(self):
    '''Get all lights'''
    lights = self.send_request('lights')
    return lights


  def get_light(self, light_id):
    #self.get_lights()
    if isinstance(light_id, int):
      for light in self._lights:
        if light.light_id == light_id:
          return light

    for light in self._lights:
      if light.name == light_id:
        return light

  def get_light_control(self, light_id):
    return Light(self.get_light(light_id))

  def get_all_light_controls(self):
    #self.get_lights()
    all_lights = {}
    for light in self._lights:
      all_lights[light._name] = self.get_light_control(light._name)
    return all_lights




  def get_groups(self):
    '''Get all groups'''
    groups = self.send_request('groups')
    return groups

  def get_group(self, group_id):
    #self.get_groups()
    if isinstance(group_id, int):
      for group in self._groups:
        if group.group_id == group_id:
          return group

    for group in self._groups:
      if group.name == group_id:
        return group

  def get_group_control(self, group_id):
    return Group(self.get_group(group_id))

  def get_all_group_controls(self):
    self.get_lights()
    all_groups = {}
    for group in self._groups:
      all_groups[group._name] = self.get_group_control(group._name)
    return all_groups


  def update(self):
    self.get_lights()
    self.get_groups()