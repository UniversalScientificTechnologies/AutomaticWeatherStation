#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rosgraph
import rospy
import os
import sys
from arom.srv import *
from arom.msg import *

class AromNode():
    def __init__(self):
        try:
            rosgraph.Master('/rostopic').getPid()
        except Exception, e:
            print ("Unable to communicate with master!")
            print ("Try start ROSCORE or ROSLAUNCH some project")
            sys.exit(0)
            #raise e

        try:
            if self.node_pymlab:
                #self.pymlabService = rospy.ServiceProxy('pymlab_drive', PymlabDrive)
                self.pymlab = rospy.ServiceProxy('pymlab_drive', PymlabDrive)
                rospy.set_param('/arom/node'+rospy.get_name()+"/pymlab", True)
            else:
                rospy.set_param('/arom/node'+rospy.get_name()+"/pymlab", False)
        except Exception, e:
            print rospy.get_name()
            rospy.set_param('/arom/node'+rospy.get_name()+"/pymlab", False)

        print "Starting init"
        rospy.init_node(self.node_name)
        rospy.set_param('/arom/node'+rospy.get_name()+"/type", self.node_type)
        self.node_name = rospy.get_name()
        print "Init done:", rospy.get_name()

    #def pymlab(self, *args, **kwds):
    #    self.pymlabService(**kwds)

    def set_feature(self, name, value):
        rospy.set_param('/arom/node%s/feature/%s' %(str(rospy.get_name()),name), value)
        rospy.loginfo("New feature '%s' for %s" %(rospy.get_name(), name))