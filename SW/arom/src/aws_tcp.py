#!/usr/bin/env python

import math
import time
import rospy
from arom.srv import *
from arom.msg import *
import socket
import json
import UDP


data = {}

def callback(recive):
    global data
    for i, type in enumerate(recive.type):
        data[type] = recive.value[i]
    #print data


def awsTCP():

    rospy.init_node('awsTCP', anonymous=True)
    rospy.Subscriber("/aws_out", msg_WeatherStation, callback)


    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    sock.sendto('MESSAGE', (UDP_IP, UDP_PORT))


    rate = rospy.Rate(1) # 10s
    while data == {} and not rospy.is_shutdown():
        time.sleep(0.25)
    while not rospy.is_shutdown():
        print json.dumps(data)
        sock.sendto(json.dumps(data), (UDP_IP, UDP_PORT))
        UDP.send("Hello, world!", "239.192.0.100", 1000)
        rate.sleep()


if __name__ == '__main__':
    awsTCP()