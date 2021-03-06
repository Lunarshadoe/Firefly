# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 21:48:42
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-12 23:01:32


import logging
import requests

from core.models.device import Device

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Pushover Notifications',
      'author' : 'Zachary Priddy',
      'commands' : ['notify'],
      'capabilities' : ['notify'],
      'module' : 'ffPushover'
    }
    
    self.COMMANDS = {
      'notify' : self.notify
    }

    self.REQUESTS = {
    }

    self.VIEWS = {}

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._api_key = args.get('api_key')
    self._user_key = args.get('user_key')

    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################

#############################################################

  @property
  def api_key(self):
      return self._api_key

  @property
  def user_key(self):
      return self._user_key

  def notify(self, args):
    post_data = {
      'token':self.api_key,
      'user' : self.user_key,
      'title' : 'Firefly Notification',
      'message' : args.get('message'),
      'priority' : 0
    }

    if args.get('priority'):
      if args.get('priority') == 'low':
        post_data['priority'] = -1
      if args.get('priority') == 'high':
        post_data['priority'] = 1
      if args.get('priority') == 'emergency':
        post_data['priority'] = 2
        post_data['retry'] = '60'
        post_data['expire'] = '3600'

    if args.get('device'):
      post_data['device'] = args.get('device')

    requests.post('https://api.pushover.net/1/messages.json', data=post_data)


  def print_response_code(self, response):
    logging.debug('Pushover Response: ' + str(response))