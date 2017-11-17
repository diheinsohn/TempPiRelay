import os
import time
import datetime
import glob
import serial
import MySQLdb
from time import strftime
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
#temp_sensor = '/sys/bus/w1/devices/28-00000622fd44/w1_slave'
sensor_temp = '/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_75439323735351B09120-if00'
ser = serial.Serial(sensor_temp,9600)

# Variables for MySQL
db = MySQLdb.connect(host="201.148.104.6", user = "cervece1" ,passwd="O8bub97n1A", db="cervece1_temp")
cur = db.cursor() 
text_file = open("output.txt", "w")
count = 0

def tempRead():
    lines = ser.readline()
    print lines
    
    try:
	temp_c = float(lines)
    except Exception, e:
	temp_c = 0
	print "Error: " + str(e)	

    return round(temp_c,2)
 
while count < 100:
    temp = tempRead()
    print temp
    datetimeWrite = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))
    print datetimeWrite
    sql = ("""INSERT INTO tempLog (datetime,temp) VALUES (%s,%s)""",(datetimeWrite,temp))
    try:
        print "Escribiendo en la BD..."
        # Execute the SQL command
        cur.execute(*sql)
        # Commit your changes in the database
        db.commit()
        text_file.write(datetimeWrite + " // " +str(temp)+ "\n")
        print "Completo."
 
    except Exception, e:
        # Rollback in case there is any error
        #db.rollback()
        print "Error :" + str(e)
    count += 1

cur.close()
db.close()

