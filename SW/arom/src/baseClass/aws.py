#!/usr/bin/env python

import math
import time
import rospy
import std_msgs
import actionlib
import json
from std_msgs.msg import String
from std_msgs.msg import Float32
from arom.srv import *
from arom.msg import *
import numpy as np



class weatherStation(object):
    def __init__(self, parent = None, arg = None, name = "weatherStation", port="", connect = True, var = {}):
        self.arg = arg
        self.Autoconnect = connect
        self.port = port
        self.parent = parent
        self.name = name
        self.sname = self.name
        self.variables = var
        self.rate = 1
        

        ##
        ##  Inicializace vlastniho ovladace
        ##

        self.init()

        #_RegisterDriver = rospy.Service('driver/weatherStation/%s' %self.name, arom.srv.DriverControl, self.reset)

        self.pub_weather = rospy.Publisher('aws_out', msg_WeatherStation, queue_size=10)

        rospy.init_node('AROM_weatherStation')
        #rospy.loginfo("%s: wait_for_service: 'arom/RegisterDriver'" % self.name)
        #rospy.wait_for_service('arom/RegisterDriver')
        #rospy.loginfo("%s: >> brain found" % self.name)

        ##
        ##  Registrace zarizeni
        ##  >Arom returns 1 - OK, 0 - False
        ##

        #RegisterDriver = rospy.ServiceProxy('arom/RegisterDriver', arom.srv.RegisterDriver)
        #registred = RegisterDriver(name = self.name, sname = self.name, driver = self.arg['driver'], device = self.arg['type'], service = 'arom/driver/%s/%s' %(self.arg['type'], self.name), status = 1)
        #rospy.loginfo("%s: >> register %s driver: %s" %(self.name, 'AWS01A', registred))


        ##
        ##  Ovladac se pripoji k montazi
        ##

        if self.Autoconnect:
            self.connect()

        ##
        ##  Ovladac pujde ukoncit
        ##

        rate = rospy.Rate(self.rate)
        while not rospy.is_shutdown():
            try:
                data = self.mesure()
                self.send(data)
            except Exception, e:
                rospy.logerr(e)
            rate.sleep()


        self.connection.close()

    def reset(self, val=None):
        pass

    def send(self, data):
        print data
        msg_data = msg_WeatherStation()
        msg_data.type = data[0]
        msg_data.value = data[1]
        self.pub_weather.publish(msg_data)

    def datalog(self, val = []):
        for row in val:
            print row
            #self._sql("INSERT INTO `AROM`.`weather` (`date`, `type_id`, `sensors_id`, `value`) VALUES ('%f', '%i', '%i', '%f');" % (row['time'], 0, 0, row['value']))
            #self._sql("INSERT INTO `AROM`.`weather` (`date`, `type_id`, `sensors_id`, `value`) VALUES ('%f', %i, (SELECT sensors_id FROM sensors WHERE sensor_name = '%s'), '%f');" % (row['time'], 0, row['name'], row['value']))
        pass
