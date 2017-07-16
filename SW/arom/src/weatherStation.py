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
import serial
from astropy.time import Time
import astropy.units as u
import MySQLdb as mdb
import httplib2





def calc_dewpoint(temp, hum):
    x = 1 - 0.01 * hum;

    dewpoint = (14.55 + 0.114 * temp) * x;
    dewpoint = dewpoint + ((2.5 + 0.007 * temp) * x) ** 3;
    dewpoint = dewpoint + (15.9 + 0.117 * temp) * x ** 14;
    dewpoint = temp - dewpoint;

    return dewpoint





class weatherStation(object):
    def __init__(self, parent = None, arg = None, name = "weatherStation", port="", connect = True, var = {}):
        self.arg = arg
        self.Autoconnect = connect
        self.port = port
        self.parent = parent
        self.name = self.arg['name']
        self.sname = self.name
        self.variables = var
        
        ##
        ##  Pripojeni k databazi
        ##

        self.connection = mdb.connect(host="localhost", user="root", passwd="root", db="AROM", use_unicode=True, charset="utf8")
        self.cursorobj = self.connection.cursor()

        ##
        ##  Inicializace vlastniho ovladace
        ##

        self.init()

        s_RegisterDriver = rospy.Service('driver/weatherStation/%s' %self.name, arom.srv.DriverControl, self.reset)

        ##
        ##  Ceka to na spusteni AROMbrain nodu
        ##

        rospy.init_node('AROM_weatherStation')
        rospy.loginfo("%s: wait_for_service: 'arom/RegisterDriver'" % self.name)
        rospy.wait_for_service('arom/RegisterDriver')
        rospy.loginfo("%s: >> brain found" % self.name)

        ##
        ##  Registrace zarizeni
        ##  >Arom returns 1 - OK, 0 - False
        ##

        RegisterDriver = rospy.ServiceProxy('arom/RegisterDriver', arom.srv.RegisterDriver)
        registred = RegisterDriver(name = self.name, sname = self.name, driver = self.arg['driver'], device = self.arg['type'], service = 'arom/driver/%s/%s' %(self.arg['type'], self.name), status = 1)
        rospy.loginfo("%s: >> register %s driver: %s" %(self.name, 'AWS01A', registred))


        ##
        ##  Ovladac se pripoji k montazi
        ##

        if self.Autoconnect:
            self.connect()

        ##
        ##  Ovladac pujde ukoncit
        ##

        rate = rospy.Rate(0.1)
        while not rospy.is_shutdown():
            try:
                data = self.mesure()
                self.datalog(data)
            except Exception, e:
                rospy.logerr(e)
            rate.sleep()


        self.connection.close()

    def _sql(self, query, read=False):
        #print query
        result = None
        try:
            self.cursorobj.execute(query)
            result = self.cursorobj.fetchall()
            if not read:
                self.connection.commit()
        except Exception, e:
            rospy.logerr("MySQL: %s" %repr(e))
        return result

    def reset(self, val=None):
        pass

    def datalog(self, val = []):
        for row in val:
            #self._sql("INSERT INTO `AROM`.`weather` (`date`, `type_id`, `sensors_id`, `value`) VALUES ('%f', '%i', '%i', '%f');" % (row['time'], 0, 0, row['value']))
            self._sql("INSERT INTO `AROM`.`weather` (`date`, `type_id`, `sensors_id`, `value`) VALUES ('%f', %i, (SELECT sensors_id FROM sensors WHERE sensor_name = '%s'), '%f');" % (row['time'], 0, row['name'], row['value']))
        pass



###############################################################################################################################################################################
#################################################################################################################################################################################
#################################################################################################################################################################################
#################################################################################################################################################################################
#################################################################################################################################################################################

class weatherDataUploader(object):
    def __init__(self, parent = None, arg = None, name = "weatherDataUploader", var = {}):
        self.arg = arg
        self.name = self.arg['name']
        self.sname = self.name
        self.variables = var
        
        ##
        ##  Pripojeni k databazi
        ##

        self.connection = mdb.connect(host="localhost", user="root", passwd="root", db="AROM", use_unicode=True, charset="utf8")
        self.cursorobj = self.connection.cursor()

        ##
        ##  Inicializace vlastniho ovladace
        ##

        self.init()

        s_RegisterDriver = rospy.Service('driver/weatherStation/%s' %self.name, arom.srv.DriverControl, self.reset)

        ##
        ##  Ceka to na spusteni AROMbrain nodu
        ##

        rospy.init_node('AROM_weatherUploader')
        rospy.loginfo("%s: wait_for_service: 'arom/RegisterDriver'" % self.name)
        rospy.wait_for_service('arom/RegisterDriver')
        rospy.loginfo("%s: >> brain found" % self.name)

        ##
        ##  Registrace zarizeni
        ##  >Arom returns 1 - OK, 0 - False
        ##

        RegisterDriver = rospy.ServiceProxy('arom/RegisterDriver', arom.srv.RegisterDriver)
        registred = RegisterDriver(name = self.name, sname = self.name, driver = self.arg['driver'], device = self.arg['type'], service = 'arom/driver/%s/%s' %(self.arg['type'], self.name), status = 1)
        rospy.loginfo("%s: >> register %s driver: %s" %(self.name, 'AWS01A', registred))


        ##
        ##  Ovladac se pripoji k montazi
        ##


        ##
        ##  Ovladac pujde ukoncit
        ##

        rate = rospy.Rate(0.1)
        while not rospy.is_shutdown():
            try:
                values = self._sql('SELECT ROUND(weather.date), weather.value, sensors.sensor_name, sensors.sensor_quantity_type, sensors.sensor_field_quantity_type, sensors.sensor_field_name FROM weather JOIN sensors ON weather.sensors_id = sensors.sensors_id WHERE weather.date > %f GROUP BY weather.sensors_id ORDER BY weather.date DESC;' %(Time.now().unix-30))
                data = self.datapush(values)
            except Exception, e:
                rospy.logerr(e)
            time.sleep(30)

        self.connection.close()

    def _sql(self, query, read=False):
        #print query
        result = None
        try:
            self.cursorobj.execute(query)
            result = self.cursorobj.fetchall()
            if not read:
                self.connection.commit()
        except Exception, e:
            rospy.logerr("MySQL: %s" %repr(e))
        return result

    def reset(self, val=None):
        pass

    def transform(self, value, inT, outT):
        if inT =='C':
            if outT == 'F':
                return value*1.8+32.00
            else:
                return value
        elif inT =='MS':
            if outT == 'MPS':
                return (value*2.2369362920544)
            else:
                return value
        else:
            return value




###############################################################################################################################################################################
#################################################################################################################################################################################
#################################################################################################################################################################################
#################################################################################################################################################################################
#################################################################################################################################################################################

class AntiDewSystem(object):
    def __init__(self, parent = None, arg = None, name = "AntiDewSystem", var = {}):
        self.arg = arg
        self.name = self.arg['name']
        self.sname = self.name
        self.variables = var
        self.groups = []
        
        ##
        ##  Pripojeni k databazi
        ##

        self.connection = mdb.connect(host="localhost", user="root", passwd="root", db="AROM", use_unicode=True, charset="utf8")
        self.cursorobj = self.connection.cursor()

        ##
        ##  Inicializace vlastniho ovladace
        ##

        self.init()

        s_RegisterDriver = rospy.Service('driver/weatherStation/%s' %self.name, arom.srv.DriverControl, self.reset)

        ##
        ##  Ceka to na spusteni AROMbrain nodu
        ##

        rospy.init_node('AROM_antiDewSystem')
        rospy.loginfo("%s: wait_for_service: 'arom/RegisterDriver'" % self.name)
        rospy.wait_for_service('arom/RegisterDriver')
        rospy.loginfo("%s: >> brain found" % self.name)

        ##
        ##  Registrace zarizeni
        ##  >Arom returns 1 - OK, 0 - False
        ##

        RegisterDriver = rospy.ServiceProxy('arom/RegisterDriver', arom.srv.RegisterDriver)
        registred = RegisterDriver(name = self.name, sname = self.name, driver = self.arg['driver'], device = self.arg['type'], service = 'arom/driver/%s/%s' %(self.arg['type'], self.name), status = 1)
        rospy.loginfo("%s: >> register %s driver: %s" %(self.name, 'AWS01A', registred))

        ##
        ##  Ovladac pujde ukoncit
        ##
        
        self.groups = self._sql('SELECT dd_group_id, dd_sensor_name, dd_sensor_type, dd_heater_name, dd_heater_type, dd_mode_id, dd_mode_param FROM AROM.dewdeffender;')
        print self.groups
        device = {}
        for group in self.groups:
            device[str(group[0])] = self.dd_group(group, self.pymlab, self._sql)

        rate = rospy.Rate(0.5)
        while not rospy.is_shutdown():
            try:
                for group in self.groups:
                    print group
                    device[str(group[0])].renew()
            except Exception, e:
                rospy.logerr(e)
            #time.sleep(30)
            rate.sleep()

        self.connection.close()


    def _sql(self, query, read=False):
        #print query
        result = None
        try:
            self.cursorobj.execute(query)
            result = self.cursorobj.fetchall()
            if not read:
                self.connection.commit()
        except Exception, e:
            rospy.logerr("MySQL: %s" %repr(e))
        return result

    def reset(self, val=None):
        pass



############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################

######################################################################################
######################################################################################
##                                                                                  ##
##                  Driver for --AWS01A-- MLAB weather station                      ##
##                 ============================================                     ##
##                                                                                  ##
##                                                                                  ##
######################################################################################
        
class AWS01B(weatherStation):
    def init(self): 
        self.variables = {
            'AWS_LTS_temp': 0,
            'AWS_SHT_temp': 0,
            'AWS_SHT_humi': 0
            }
        rospy.loginfo("AWS01A weather station requires 'pymlab_drive' service from 'ROSpymlabServer' node")
        rospy.loginfo("run>> 'rosrun arom initPymlab.py'")
        rospy.wait_for_service('pymlab_drive')
        self.pymlab = rospy.ServiceProxy('pymlab_drive', PymlabDrive)
        rospy.loginfo("%s: >> 'ROSpymlabServer' found" % self.name)
        self.last_wind_mes = Time.now()


    def mesure(self):

    # LTS -- ref temp
        data = self.pymlab(device="AWS_temp_ref", method="get_temp").value
        print data
        AWS_LTS_temp_ref = eval(data)
        #self.variables['AWS_LTS_temp_ref'] = AWS_LTS_temp_ref

    # SHT31
        TempHum = eval(self.pymlab(device="AWS_humi", method="get_TempHum", parameters=None).value)
        #self.variables['AWS_AMBIENT_temp'] = TempHum[0]
        #self.variables['AWS_AMBIENT_humi'] = TempHum[1]

    # SHT25
        InTemp = eval(self.pymlab(device="AWS_humi_in", method="get_temp_8bit", parameters=None).value)
        InHum = eval(self.pymlab(device="AWS_humi_in", method="get_hum_8bit", parameters=None).value)
        #self.variables['AWS_AMBIENT_temp'] = TempHum[0]
        #self.variables['AWS_AMBIENT_humi'] = TempHum[1]

    # WIND

        #rospy.set_param("weatherStation", str(self.variables))
        rospy.loginfo('LTS: %s, sht31.temp: %s, sht31.humi: %s' %(str(AWS_LTS_temp_ref), str(TempHum[0]), str(TempHum[1])))

        angles = np.zeros(5)
        angles[4] = eval(self.pymlab(device="AWS_wind_s", method="get_angle", parameters='').value)
        time.sleep(0.01)
        angles[3] = eval(self.pymlab(device="AWS_wind_s", method="get_angle", parameters='').value)
        time.sleep(0.01)
        angles[2] = eval(self.pymlab(device="AWS_wind_s", method="get_angle", parameters='').value)
        time.sleep(0.01)
        angles[1] = eval(self.pymlab(device="AWS_wind_s", method="get_angle", parameters='').value)
        n = 0
        speed = 0
        AVERAGING = 50

        for i in range(AVERAGING):
            time.sleep(0.01)
            angles[0] = eval(self.pymlab(device="AWS_wind_s", method="get_angle", parameters='').value)
            
            if (angles[0] + n*360 - angles[1]) > 300:
                n -= 1
                angles[0] = angles[0] + n*360

            elif (angles[0] + n*360 - angles[1]) < -300:  # compute angular speed in backward direction.
                n += 1
                angles[0] = angles[0] + n*360

            else:
                angles[0] = angles[0] + n*360
            
            speed += (-angles[4] + 8*angles[3] - 8*angles[1] + angles[0])/12
            angles = np.roll(angles, 1)

        eval(self.pymlab(device="AWS_wind_d", method="route", parameters='').value)
        (x, y, z) = eval(self.pymlab(device="AWS_wind_d", method="axes", parameters='').value)

        if y>0:
            wind_az = 90.0 - math.atan2(x,y)*180.0/math.pi
        if y<0:
            wind_az = 270.0- math.atan2(x,y)*180.0/math.pi
        if y==0 and x<0:
            wind_az = 180.0
        if y==0 and x>0:
            wind_az = 180.0

        print " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + " DIR: " + str(wind_az)

        #speed = speed/AVERAGING             # apply averaging on acummulated value.
        
        data_time = Time.now().unix
        return [{'value':AWS_LTS_temp_ref, 'name':'AWS_telescope_temp_lts_ref', 'guantity': 'C', 'time': data_time},
                {'value':TempHum[0], 'name':'AWS_ambient_temp_2m', 'guantity': 'C', 'time': data_time},
                {'value':TempHum[1], 'name':'AWS_ambient_humi', 'guantity': 'perc', 'time': data_time},
                {'value':InTemp, 'name':'AWS_in_temp', 'guantity': 'C', 'time': data_time},
                {'value':InHum, 'name':'AWS_in_hum', 'guantity': 'perc', 'time': data_time},
                {'value':speed*(1/5000), 'name':'AWS_ambient_wind_speed_5m', 'guantity': 'ms-1', 'time': data_time},
                {'value':wind_az, 'name':'AWS_ambient_wind_direction_5m', 'guantity': 'ms-1', 'time': data_time},
                {'value':calc_dewpoint(AWS_LTS_temp_ref, TempHum[1]), 'name':'AWS_ambient_dewpoint', 'guantity': 'C', 'time': data_time}]



    def connect(self):
        pass
############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################

######################################################################################
######################################################################################
##                                                                                  ##
##                  Driver for --WEATHERCLOUD--                                     ##
##                 ============================================                     ##
##                                                                                  ##
##                                                                                  ##
######################################################################################
        
class WEATHERUNDERGROUND(weatherDataUploader):
    def init(self):
        pass

    def connect(se):
        pass

    def datapush(self, data):
        req = "?ID=%s&PASSWORD=%s&dateutc=now" %(self.arg['id'], self.arg['pass'])
        for row in data:
            #print row
            try:
                val = float(row[1])
                sourceType = row[3]
                outType = row[4]
            except Exception, e:
                print e

            req += "&"+row[5]+"="+str(self.transform(val, sourceType, outType))
        print "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"+req
        resp, content = httplib2.Http().request("http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"+req)

############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################
############################################################################################################################################################################

######################################################################################
######################################################################################
##                                                                                  ##
##                  Driver for --DewDeffender--                                     ##
##                 ============================================                     ##
##                                                                                  ##
##                                                                                  ##
######################################################################################
        
class DEWDEFF01A(AntiDewSystem):
    def init(self):
        rospy.loginfo("AWS01A weather station requires 'pymlab_drive' service from 'ROSpymlabServer' node")
        rospy.loginfo("run>> 'rosrun arom initPymlab.py'")
        rospy.wait_for_service('pymlab_drive')
        self.pymlab = rospy.ServiceProxy('pymlab_drive', PymlabDrive)

    def connect(self):
        pass

    class dd_group():
        # trida starajici se o jednu skupinu zarizeni
        def __init__(self, device, pymlab, _sql):
            self.pymlab = pymlab
            self.device = device
            self._sql = _sql
            print device
            self.pid = eval(device[6])['pid']
            print self.pid
            self.pid_integral = 0
            self.pid_last = 0
            self.pid_out = 0
            self.pymlab(device=self.device[3], method="set_ls0", parameters=str((0b11111111)))
            self.pymlab(device=self.device[3], method="set_ls1", parameters=str((0b10101010)))
            self.pymlab(device=self.device[3], method="set_pwm0", parameters=str((100, 100-0)))
            self.pymlab(device=self.device[3], method="set_pwm1", parameters=str((100, 100-0)))

        def pidCalc(self, actual, target):
            error = target - actual

            if abs(error) < 100:
                self.pid_integral = self.pid_integral + error
            else:
                self.pid_integral = 0
            P = error * self.pid[0]
            I = self.pid_integral * self.pid[1]
            D = (self.pid_last-actual) * self.pid[2]
            self.pid_out = P + I + D
            self.pid_out = self.pid_out * 1

            if self.pid_out>100:
                self.pid_out=100
            elif self.pid_out<0:
                self.pid_out=0

            self.pid_last = actual #// save current value for next time
            self.pymlab(device=self.device[3], method="set_pwm0", parameters=str((100, 100-self.pid_out)))
            self.pymlab(device=self.device[3], method="set_pwm1", parameters=str((100, 100-self.pid_out)))


        def renew(self):
            if self.device[5] == 0:
                print self.device[1]
                Temp = float(self._sql('SELECT value FROM weather where sensors_id = 8 ORDER BY id DESC LIMIT 1;')[0][0])
                Hum = float(self._sql('SELECT value FROM weather where sensors_id = 3 ORDER BY id DESC LIMIT 1;')[0][0])
                lTemp = eval(self.pymlab(device=self.device[1], method="get_temp_8bit", parameters=None).value)
                #Hum = eval(self.pymlab(device=self.device[1], method="get_hum_8bit", parameters=None).value)
                dew = calc_dewpoint(Temp, Hum)
                self.pidCalc(lTemp, Temp+50)

                print lTemp, Temp+50, Hum, dew, self.pid_out
        

    

if __name__ == '__main__':
    cfg = rospy.get_param("ObservatoryConfig/file")
    with open(cfg) as data_file:
        config = json.load(data_file)
    for x in config:
        if x['name'] == sys.argv[1]:
            break
    weatherStation = locals()[x['driver']](arg = x)
    #weatherStation = AWS01B()