#!/usr/bin/env python

import math
import time
import rospy
from arom.srv import *
from arom.msg import *
import httplib2
import urllib


data = {}

def callback(recive):
    global data
    for i, type in enumerate(recive.type):
        data[type] = recive.value[i]
    print data


def weatherUploader():
    name = 'aws_weathercloud'
    rospy.init_node(name, anonymous=True)
    rospy.Subscriber("/aws_out", msg_WeatherStation, callback)

    wid = rospy.get_param('/arom/aws/%s/wid'%(name))
    key = rospy.get_param('/arom/aws/%s/key'%(name))


    rate = rospy.Rate(0.01) # 10hz
    while data == {} and not rospy.is_shutdown():
        time.sleep(0.25)
    while not rospy.is_shutdown():
        try:
            post_data = {'name':"ZVPP",
                         'ver': '001',
                         'wid': wid,
                         'key': key,
                         'time': time.strftime("%H%M", time.localtime()),
                         'bar': int(data['pressureAWS']*0.1),
                         'hum': int(data['humidityAWS0']*1),
                         'temp': int(data['temperatureAWS0']*10),
                         'dew': int(data['dewpointAWS']*10),
                         'wspd': int(data['windspdAWS']*10),
                         'wdir': int(data['winddirAWS']*1),
                         'solarrad': int(data['lightAWS']*10),
                         }


            rospy.loginfo("Uploading data to weathercloud.net: %s" %repr(post_data))
            print httplib2.Http().request("http://api.weathercloud.net/v01/set?" + urllib.urlencode(post_data), 'GET')

        except Exception, e:
            rospy.logerr(e)
        rate.sleep()


if __name__ == '__main__':
    weatherUploader()