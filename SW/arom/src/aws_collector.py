#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import time
import math
from arom.srv import *
from arom.msg import *
from baseClass.aws import weatherStation

def calc_dewpoint(temp, hum):
    x = 1 - 0.01 * hum;

    dewpoint = (14.55 + 0.114 * temp) * x;
    dewpoint = dewpoint + ((2.5 + 0.007 * temp) * x) ** 3;
    dewpoint = dewpoint + (15.9 + 0.117 * temp) * x ** 14;
    dewpoint = temp - dewpoint;

    return dewpoint

class aws_collector(weatherStation):
    def init(self):
        pass

    def connect(self):
        self.pymlab = rospy.ServiceProxy('pymlab_drive', PymlabDrive)
        self.last_wind_mes = time.time()
        self.connection = True


    def mesure(self):
        temperatureAWS0     = eval(self.pymlab(device="AWS_temp_ref", method="get_temp").value) # LTS
        temperatureTEL0     = eval(self.pymlab(device="telescope_lts", method="get_temp").value) # LTS
        (temperatureAWS1, humidityAWS0) = eval(self.pymlab(device="AWS_humi",     method="get_TempHum").value) # SHT31
        windspdAWS          = eval(self.pymlab(device="AWS_wind_s",   method="get_speed").value) # RPS
        (x, y, z)           = eval(self.pymlab(device="AWS_wind_d",   method="axes").value) # MAG
        lightAWS            = eval(self.pymlab(device="AWS_light",     method="get_lux").value) # ISL03
        (temperatureAWS2, pressureAWS) = eval(self.pymlab(device="AWS_press",   method="get_tp").value) # ALTIMET
        #clouds = self.pymlab(device="AWS_clouds", method="getRawData").value
        #clouds2 = self.pymlab(device="AWS_clouds", method="getTambient").value
        #print "#####", clouds, x, y, z
        if y > 0:
            winddirAWS = 90 - (math.atan(x/y))*180.0/math.pi
        elif y < 0:
            winddirAWS = 270 - (math.atan(x/y))*180.0/math.pi
        elif y == 0 & x < 0:
            winddirAWS =  180.0
        elif y == 0 & x > 0:
            winddirAWS = 0.0


        type = ["temperatureAWS1", "temperatureAWS0", "dewpointAWS", "humidityAWS0", "windspdAWS", "winddirAWS", "lightAWS", "temperatureAWS2", "pressureAWS", "temperatureTEL0"]
        data = [temperatureAWS1, temperatureAWS0, calc_dewpoint(temperatureAWS0, humidityAWS0), humidityAWS0, windspdAWS, winddirAWS, lightAWS, temperatureAWS2, pressureAWS, temperatureTEL0]
        print data
        return (type, data)
        

if __name__ == '__main__':
    aws = aws_collector()


