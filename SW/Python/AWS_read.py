#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class

import time
import datetime
import sys

from pymlab import config

#uncomment for debbug purposes
import logging
logging.basicConfig(level=logging.DEBUG)


#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s #I2CPORT\n" % (sys.argv[0], ))
    sys.exit(1)

port    = eval(sys.argv[1])


#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
    },

    bus = [
        {
            "type": "i2chub",
            "address": 0x72,            
            "children": [
                {
                    "type": "i2chub",
                    "address": 0x70,
                    "channel": 0,
                    "children": [
                                {"name": "barometer", "type": "altimet01" , "channel": 0, },   
                                {"name": "hum_temp", "type": "sht25" , "channel": 1, },   
#                                {"name": "wind_direction", "type": "mag01" , "channel": 1, },   
#                                {"name": "thermometer", "type": "lts01" , "channel": 2, },   
                    ], 
                },
#                {"name": "barometer2", "type": "altimet01" , "channel": 6, },
            ],
        },
    ],
)

cfg.initialize()

barometer = cfg.get_device("barometer")
hum_temp = cfg.get_device("hum_temp")
#wind_direction = cfg.get_device("wind_direction")
#thermometer = cfg.get_device("thermometer")
time.sleep(0.5)

#### Data Logging ###################################################

filename = datetime.datetime.now().isoformat()


try:
    with open(filename+".log", "a") as f:
        while True:
            barometer.route()
            (t1, p1) = barometer.get_tp()
            hum_temp.route()
            t2 = hum_temp.get_temp()
#            t3 = thermometer.get_temp()
            t3 = -200
            h1 = hum_temp.get_hum()
            

            sys.stdout.write(" Temperature: %.2f  Pressure: %d TempSHT: %.2f  HumSHT: %.1f TempLTS: %.2f" % (t1, p1, t2, h1, t3))
            f.write("%d\t%.2f\t%d\t%.2f\t%.1f\t%.2f\n" % (time.time(),t1, p1, t2, h1, t3))
            sys.stdout.flush()
            time.sleep(10)
except KeyboardInterrupt:
    sys.exit(0)

