
"""
   sudo ln aws_weewx_connector.py /usr/share/weewx/weewx/drivers/aws_arom.py
"""

import time
import logging

import weedb
import weewx.drivers
import weeutil.weeutil

import json

import rospy
import std_msgs
#from arom.srv import *
#from arom.msg import *

DRIVER_NAME = 'AWS_AROM'
DRIVER_VERSION = "0.1"


def loader(config_dict, engine):
    # This loader uses a bit of a hack to have the simulator resume at a later
    # time. It's not bad, but I'm not enthusiastic about having special
    # knowledge about the database in a driver, albeit just the loader.

    station = AWS_AROM(**config_dict)
    return station

class AWS_AROM(weewx.drivers.AbstractDevice):
    def __init__(self, **stn_dict):
        self.stn_dict = stn_dict
        print stn_dict[DRIVER_NAME]
        self.data = {}
        name = 'weewx_bridge'
        rospy.init_node(name, anonymous=False)
        rospy.set_param('/arom/node%s/feature/%s' %(str(rospy.get_name()),'weewx'), '/weewx/')
        print '/arom/node%s/feature/%s' %(str(rospy.get_name()),'weewx')
        rospy.Subscriber("/arom/node/aws", std_msgs.msg.String, self.callback)

    def callback(self, data):
        #print data.data
        self.data = json.loads(data.data)

    def genLoopPackets(self):
        while self.data == {}:
            time.sleep(0.25)
        while True: 
            #print self.data
            try:
                _packet = {"dateTime": time.time(),
                           "usUnits" : weewx.METRICWX}
                #print _packet

                Sensor_mapping = self.stn_dict[DRIVER_NAME]['Sensor_mapping']
                for sensor in self.data['sensors']:
                    try:
                        #print sensor
                        sensor_name = sensor['name']


                        if sensor_name in Sensor_mapping:
                            _packet[Sensor_mapping[sensor_name][0]] = sensor['value']*float(Sensor_mapping[sensor_name][1])
                    except Exception, e:
                        print e


                #print ">>>", _packet
                yield _packet
            except Exception, e:
                print e
            time.sleep(5)


    @property
    def hardware_name(self):
        return "AWS_AROM"


def confeditor_loader():
    return AWSConfEditor()

class AWSConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[AWS_AROM]
    # This section is for the AWS_AROM weather station

    # The driver to use:
    driver = weewx.drivers.aws_arom

    # Sensor mapping to the weewx data
    [[Sensor_mapping]]
        outTemp = barometer, 1
        # arom_sensor_name = WeeWX_data_name, multiplier
"""


if __name__ == "__main__":
    station = AWS_AROM()
    for packet in station.genLoopPackets():
        pass
