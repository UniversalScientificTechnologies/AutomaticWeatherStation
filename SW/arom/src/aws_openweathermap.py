#!/usr/bin/env python

import math
import time
import rospy
from arom.srv import *
from arom.msg import *
import httplib2

import Queue
import base64
import syslog
import urllib
import urllib2

data = {}

def callback(recive):
    global data
    for i, type in enumerate(recive.type):
        data[type] = recive.value[i]
    #print data


def openWeatherMap():
    name = 'aws_openweathermap'
    rospy.init_node(name, anonymous=True)
    rospy.Subscriber("/aws_out", msg_WeatherStation, callback)

    #ID = rospy.get_param('/arom/aws/%s/ID'%(name))
    #PASSWORD = rospy.get_param('/arom/aws/%s/PASSWORD'%(name))
    NAME = rospy.get_param('/arom/observatory/name')
    LAT = rospy.get_param('/arom/observatory/lat')
    LON = rospy.get_param('/arom/observatory/lon')
    ALT = rospy.get_param('/arom/observatory/alt')

    rate = rospy.Rate(0.01) # 10hz
    while data == {} and not rospy.is_shutdown():
        time.sleep(0.25)
    while not rospy.is_shutdown():
        try:
            
            
            
            values = {}
            #values['name'] = NAME
            values['lat']  = str(LAT)
            values['long'] = str(LON)
            values['alt']  = str(ALT)
            values['temp'] = str(14.345)

            req = urllib2.Request("http://openweathermap.org/data/post/", urllib.urlencode(values))
            req.get_method = lambda: 'POST'
            #req.add_header("User-Agent", "arom/aws_openweathermap")
            b64s = base64.encodestring('%s:%s' % ('roman-dvorak', 'hesloje1')).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % b64s)
            #self.post_with_retries(req)
            print req.get_full_url()
            print req.get_type()
            print req.get_selector()
            print b64s
            print req.get_header('Authorization')
            response = urllib2.urlopen(req)

            print response

        except urllib2.HTTPError, e:
          if e.getcode() == 500:
            content = e.read()
            print content
          else:
            rospy.logerr(e)
          
        rate.sleep()


if __name__ == '__main__':
    openWeatherMap()