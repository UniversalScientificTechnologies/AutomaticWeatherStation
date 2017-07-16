#!/usr/bin/env python

import math
import time
import rospy
from arom.srv import *
from arom.msg import *
from std_msgs.msg import String
import httplib2

from __init__ import AromNode

data = {}

def callback(recive):
    global data
    for i, type in enumerate(recive.type):
        data[type] = recive.value[i]
    #print data

def update_parameters(recive):
    data = eval(recive.data)
    print '/arom/node%s/feature/aws_uploader_api_params/data/%s/%s/' %(rospy.get_name(), data['id'], 'value')
    rospy.set_param('/arom/node%s/feature/aws_uploader_api_params/data/%s/%s/' %(rospy.get_name(), data['id'], 'value'), data['source'])

class weatherUploader(AromNode):
    node_name = "aws_weatherudnerground"
    node_type = "aws_uploader"
    node_pymlab = False

    def __init__(self):
        rospy.Subscriber("/aws_out", msg_WeatherStation, callback)
        rospy.Subscriber("/%s/update_parameters"%(self.node_name), String, update_parameters)
        ID = rospy.get_param('/arom/aws/%s/ID'%(self.node_name))
        PASSWORD = rospy.get_param('/arom/aws/%s/PASSWORD'%(self.node_name))

        AromNode.__init__(self)
        self.UpdateFeature()

        rate = rospy.Rate(0.2) # 10hz
        while data == {} and not rospy.is_shutdown():
            time.sleep(0.25)
        while not rospy.is_shutdown():
            try:
                self.UpdateFeature()
                req = ""
                types = rospy.get_param('/arom/node/aws_weatherudnerground/feature/aws_uploader_api_params/data/')
                for preset in self.aws_preset:
                    try:
                        req += "&%s=%s" %(str(self.aws_preset[preset]), preset)

                    except Exception, e:
                        rospy.loginfo("#1> " + repr(e))

                for sensor in data:
                    try:
                        req += "&%s=%f" %(self.aws_data[sensor], self.ConvertValue(float(data[sensor]), self.api_data[self.aws_data[sensor]]['unit']))
                        
                    except Exception, e:
                        rospy.loginfo("#2> " + repr(e))
                
                #print req

                print "https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php?realtime=1&rtfreq=5"+req

                #resp, content = httplib2.Http().request("http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"+req)
                resp, content = httplib2.Http().request("https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php?realtime=1&rtfreq=5"+req)
            except Exception, e:
                rospy.logerr(e)

            rate.sleep()

    def ConvertValue(self, value, outUnit, multiply = 1):
        if outUnit == 'fahrenheit':
            print "CALC FAHRENHEIT"
            calc = value * 9/5 + 32
        else:
            print "NO CALC"
            calc = value

        return calc*multiply



    def UpdateFeature(self):
        self.aws_data = {}
        self.aws_preset={}
        self.api_data = rospy.get_param('/arom/node%s/feature/aws_uploader_api_params/data' %(str(rospy.get_name())), False)
        print self.api_data
        if not self.api_data:
            self.api_data = {'action':{'type': 'static', 'when': 'always', 'value': 'updateraw'},
                    'ID':   {'type': 'preset', 'when': 'always'},
                    'PASSWORD':{'type': 'preset', 'when': 'always'},
                    'softwaretype': {'type': 'static', 'when': 'always', 'value': 'AROM-Autonomou-robotic-observatory-manager'},
                    'dateutc': {'type': 'static', 'when': 'always', 'value': 'now'},

                    'winddir': {'type': 'data', 'when': '0;360', 'unit': 'degree', 'multiply': 1},
                    'windspeedmph': {'type': 'data', 'when': '0;200', 'unit': 'mph', 'multiply': 1},
                    'windgustmph': {'type': 'data', 'when': '0;200', 'unit': 'mph', 'multiply': 1},
                    'windgustdir': {'type': 'data', 'when': '0;360', 'unit': 'degree', 'multiply': 1},
                    'windspdmph_avg2m': {'type': 'data', 'when': '0;200', 'unit': 'mph', 'multiply': 1},
                    'winddir_avg2m': {'type': 'data', 'when': '0;360', 'unit': 'degree', 'multiply': 1},
                    'windgustdir_10m': {'type': 'data', 'when': '0;360', 'unit': 'degree', 'multiply': 1},
                    'humidity': {'type': 'data', 'when': '0;100', 'unit': 'percentage', 'multiply': 1},
                    'dewptf': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'tempf': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'rainin': {'type': 'data', 'when': '0;100', 'unit': 'inch', 'multiply': 1},
                    'dailyrainin': {'type': 'data', 'when': '0;100', 'unit': 'inch', 'multiply': 1},
                    'baromin': {'type': 'data', 'when': '500;1500', 'unit': 'pressure', 'multiply': 1},
                    'weather': {'type': 'data', 'unit': 'text', 'multiply': 1},
                    'clouds': {'type': 'data', 'unit': 'text', 'multiply': 1},
                    'soiltempf':  {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soiltemp2f': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soiltemp3f': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soiltemp4f': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soiltemp5f': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soilmoisture':  {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soilmoisture2': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soilmoisture3': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soilmoisture4': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'soilmoisture5': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    'leafwetness':  {'type': 'data', 'when': '0;100', 'unit': 'percentage', 'multiply': 1},
                    'leafwetness2': {'type': 'data', 'when': '0;100', 'unit': 'percentage', 'multiply': 1},
                    'solarradiation': {'type': 'data', 'when': '0;1000', 'unit': 'wpm', 'multiply': 1},
                    'UV': {'type': 'data', 'when': '0;10', 'unit': 'index', 'multiply': 1},
                    'visibility': {'type': 'data', 'when': 'always', 'unit': 'miles', 'multiply': 1},
                    'indoorhumidity': {'type': 'data', 'when': '0;100', 'unit': 'percentage', 'multiply': 1},
                    'indoortempf': {'type': 'data', 'when': '-40;120', 'unit': 'fahrenheit', 'multiply': 1},
                    }
            self.set_feature('aws_uploader_api_params',{'data': self.api_data})

        for value in self.api_data:
            if self.api_data[value]['type'] == 'data' and 'value' in self.api_data[value]:
                self.aws_data[self.api_data[value]['value']] = value
            elif (self.api_data[value]['type'] == 'preset' or self.api_data[value]['type'] == 'static') and 'value' in self.api_data[value]:
                self.aws_preset[self.api_data[value]['value']] = value

        #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^66"
        #print self.aws_data
        #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^66"
        #print self.aws_preset





if __name__ == '__main__':
    weatherUploader()





'''
action [action=updateraw] -- always supply this parameter to indicate you are making a weather observation upload
ID [ID as registered by wunderground.com]
PASSWORD [Station Key registered with this PWS ID, case sensitive]
dateutc - [YYYY-MM-DD HH:MM:SS (mysql format)] In Universal Coordinated Time (UTC) Not local time
=========================
winddir - [0-360 instantaneous wind direction]
windspeedmph - [mph instantaneous wind speed]
windgustmph - [mph current wind gust, using software specific time period]
windgustdir - [0-360 using software specific time period]
windspdmph_avg2m  - [mph 2 minute average wind speed mph]
winddir_avg2m - [0-360 2 minute average wind direction]
windgustmph_10m - [mph past 10 minutes wind gust mph ]
windgustdir_10m - [0-360 past 10 minutes wind gust direction]
humidity - [% outdoor humidity 0-100%]
dewptf- [F outdoor dewpoint F]
tempf - [F outdoor temperature] (for extra outdoor sensors use temp2f, temp3f, and so on)
rainin - [rain inches over the past hour)] -- the accumulated rainfall in the past 60 min
dailyrainin - [rain inches so far today in local time]
baromin - [barometric pressure inches]
weather - [text] -- metar style (+RA)
clouds - [text] -- SKC, FEW, SCT, BKN, OVC
soiltempf - [F soil temperature]  (for sensors 2,3,4 use soiltemp2f, soiltemp3f, and soiltemp4f)
soilmoisture - [%] (for sensors 2,3,4 use soilmoisture2, soilmoisture3, and soilmoisture4)
leafwetness  - [%] (for sensor 2 use leafwetness2)
solarradiation - [W/m^2]
UV - [index]
visibility - [nm visibility]
indoortempf - [F indoor temperature F]
indoorhumidity - [% indoor humidity 0-100]
---
##Pollution Fields:
AqNO - [ NO (nitric oxide) ppb ]
AqNO2T - (nitrogen dioxide), true measure ppb
AqNO2 - NO2 computed, NOx-NO ppb
AqNO2Y - NO2 computed, NOy-NO ppb
AqNOX - NOx (nitrogen oxides) - ppb
AqNOY - NOy (total reactive nitrogen) - ppb
AqNO3 -NO3 ion (nitrate, not adjusted for ammonium ion) UG/M3
AqSO4 -SO4 ion (sulfate, not adjusted for ammonium ion) UG/M3
AqSO2 -(sulfur dioxide), conventional ppb
AqSO2T -trace levels ppb
AqCO -CO (carbon monoxide), conventional ppm
AqCOT -CO trace levels ppb
AqEC -EC (elemental carbon) - PM2.5 UG/M3
AqOC -OC (organic carbon, not adjusted for oxygen and hydrogen) - PM2.5 UG/M3
AqBC -BC (black carbon at 880 nm) UG/M3
AqUV-AETH  -UV-AETH (second channel of Aethalometer at 370 nm) UG/M3
AqPM2.5 - PM2.5 mass - UG/M3 
AqPM10 - PM10 mass - PM10 mass
AqOZONE - Ozone - ppb
softwaretype - [text] ie: WeatherLink, VWS, WeatherDisplay
'''