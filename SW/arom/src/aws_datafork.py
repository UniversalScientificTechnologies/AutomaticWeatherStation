#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import time
import rospy
from arom.srv import *
from arom.msg import *
from std_msgs.msg import String
from std_msgs.msg import Float32
import MySQLdb as mdb



data = {}

def callback(recive):
    con = mdb.connect('localhost', 'root', 'root', 'AROM');
    cur = con.cursor()
    global data
    for i, type in enumerate(recive.type):
        data[type] = recive.value[i]
        cur.execute("")

    ver = cur.fetchone()
    #print data


def awsMySQLstorage():
    name = 'aws_MySQLstorage'
    rospy.init_node(name, anonymous=True)
    rospy.Subscriber("/aws_out", msg_WeatherStation, callback)


    rate = rospy.Rate(0.01) # 10hz
    while data == {} and not rospy.is_shutdown():
        time.sleep(0.25)
    while not rospy.is_shutdown():
        try:
           
            pass
        except Exception, e:
            rospy.logerr(e)

          
        rate.sleep()


if __name__ == '__main__':
    awsMySQLstorage()