import logging

from core import deviceDB, ffScheduler, ff_zwave, routineDB
from core.models.event import Event as ffEvent
from flask import Flask

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True

from core.api.views import *

def run():
  autoStart()
  app.run(host='0.0.0.0', port=6002, threaded=True, debug=False)


def autoStart():
  with open('/opt/firefly_system/config/devices.json') as devices:
    allDevices = json.load(devices)
    logging.critical('devices: {}'.format(str(allDevices)))
    for name, device in allDevices.iteritems():
      if device.get('module') == "ffZwave":
        package_full_path = device.get('type') + 's.' + device.get('package') + '.' + device.get('module')
        package = __import__(package_full_path, globals={}, locals={}, fromlist=[device.get('package')], level=-1)
        ff_zwave.zwave = package.Device(device.get('id'), device)
        #ff_zwave.refresh_scheduler()

  for device in deviceDB.find({}):
    deviceID = device.get('id')
    ffEvent(deviceID, {'startup': True})

  ffScheduler.runEveryM(5, auto_refresh, replace=True, job_id='auto-refresh')

def auto_refresh():
  refresh_command = ffCommand('nest', 'update', source='NEST-UPDATER')

def getDeviceList(lower=True):
  logging.critical("GET DEVICE LIST")
  device_list = {}
  for d in deviceDB.find({},{"config.name":1,"id":1}):
    if d.get('config').get('name') is not None:
      if lower:
        device_list[d.get('config').get('name').lower()] = d.get('id')
      else:
        device_list[d.get('config').get('name')] = d.get('id')
  return device_list

if __name__ == "__main__":
  run()
