# -*- coding: utf-8 -*-
import os
import subprocess 
import signal
import sys
import glob 
import time
import datetime
#import MySQLdb
import RPi.GPIO as GPIO
import serial
from time import strftime

def signal_handler(signal, frame):
	subprocess.call('./cli.js reset', shell=True)
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#sys
os.system('sudo modprobe w1-gpio') 
os.system('sudo modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'

#Curvas de Ferm.
text_file = open("output8.txt", "w")
text_file2  = open("FermIPA.txt", "w")

#GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)

#variables
cont = 0
state = [0]*16
subprocess.call('./cli.js reset', shell=True)
dateTimeWrite = ""
device_folder = glob.glob(base_dir + '28*')
device_file = ["" for x in range(0,10)]
lines = ["" for x in range(0,10)]
temp_c = ["" for x in range(0,10)]
pide = [False for x in range(len(device_folder))]
for j in range(0,len(device_folder)):
	device_file[j] = device_folder[j] + '/w1_slave'

#Cervezas
fermAPA = 16
fermEPA = 16
fermIPA = 16
fermWEISS = 20
madu = 3
madug = 5
dryh = 13
diac = 20

#bools
pidiendo = False

#Base de Datos
#db = MySQLdb.connect(host="localhost", user="root", passwd="CraftTemp", db = "temp_db")
#cur = db.cursor()

def read_temp_raw():
	for i in range(0,len(device_folder)):
		f = open(device_file[i], 'r')  
		x = device_file[i]
		if x[20:-9] == "28-041652e9f5ff":
			#Estanque
			lines[9] = f.readlines()
		elif x[20:-9] == "28-04165295d4ff":
			#Ferm 6
			lines[0] = f.readlines()
		elif x[20:-9] == "28-03164712b2ff":
			#Ferm 7
			lines[1] = f.readlines()
		elif x[20:-9] == "28-031664011dff":
			#Ferm 8
			lines[2] = f.readlines()
		elif x[20:-9] == "28-0316471c43ff":
			#Ferm 10
			lines[4] = f.readlines()
		elif x[20:-9] == "28-04165299a2ff":
			#Ferm 9
			lines[3] = f.readlines()
		elif x[20:-9] == "28-03164765a5ff":
			#Ferm "3"
			lines[5] = f.readlines()
		elif x[20:-9] == "28-0316643750ff":
			#Ferm "2"
			lines[6] = f.readlines()
		elif x[20:-9] == "28-0416526e16ff":
			#Ferm "1"
			lines[7] = f.readlines()
		elif x[20:-9] == "28-041652a2c6ff":
			#Fat Mike
			lines[8] = f.readlines()
		f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	for i in range(0, len(lines)):
		print lines[i]
		if lines[i] != "":
			while lines[i][0].strip()[-3:] != 'YES':
				time.sleep(0.2)
				lines = read_temp_raw() 
			equals_pos = lines[i][1].find('t=') 
			if equals_pos != -1:
				temp_string = lines[i][1][equals_pos+2:] 
				temp_c[i] = float(temp_string) / 1000.0 
			
				# temp_f = temp_c * 9.0 / 5.0 + 32.0 
				#return temp_c, temp_f
	return temp_c

def param():
	return params

def read_config():
	dir = "/home/pi/temp/relay/config/"
	fold = glob.glob(dir + "*.txt")
	files = fold
	config = [["" for x in range(2)] for y in range(10)]
	#files = ["" for i in range(len(fold))]
	for j in range(0, len(files)):
		if "Ferm" in files[j]:
			aux = files[j]
			#print aux[31:-4]
			cont = int(aux[31:-4])-1

			f = open(files[j], 'r')
			config[cont][0] = f.readline()
			config[cont][1] = f.readline()
			f.close()
			#print(config[cont][0] + "  " + config[cont][1])
	return config


while True:
	temp = read_temp()
	#print("Ferm 1 " + str(temp[0]) +"\nFerm 2 " + str(temp[1]) + "\nFerm 3 " +str(temp[2]))
	datetimeWrite = (time.strftime("%Y-%m-%d ") + time.strftime("%H:%M:%S"))

	#Accionar Relay motor trifasico
	#if temp[0] > 25 or temp[1] > 25 or temp[2] > 25 :
	#	GPIO.output(5, GPIO.HIGH)
	#else:
	#	GPIO.output(5, GPIO.LOW)
	print('Numero de fermentadores pidiendo: ' + str(sum(state)) )
	if temp[9] > 10:
		#se apaga bomba a fermentadores
		print('Bomba recirculado apagada: Temperatura estanque mayor a 5ºC')
		if pidiendo == True:
			subprocess.call('./cli.js on 15', shell=True)
			pidiendo = False
		time.sleep(20)
	elif sum(state) == 0:
		#Se apaga bomba hacia fermentadores (ni un fermentador pide)
		print('Bomba recirculado apagada')
		if pidiendo == True:
			subprocess.call('./cli.js on 15', shell=True)
			pidiendo = False
	else:
		#se enciende bomba hacia fermentadores
		print('Bomba recirculado encendida')
		if pidiendo == False:
			subprocess.call('./cli.js off 15', shell=True)
			pidiendo = True

	#Accionar Relay electrovalvulas
	#leer config ·[0] Ferm1, [1] Ferm2, ...
	configs = read_config()
	print("Temp Estanque: " + str(temp[9]))
	for i in range(0,len(temp)):
		#Fermentacion
		print str(i) + " :" + str(temp[i])
		print configs[i]
		if "ferm" in configs[i][1] and temp[i] != "":
			if "APA" in configs[i][0]:
				if temp[i] > fermAPA and temp[9] < temp[i]:
					print "encender relay " + str(i)
					print state[i]
					if state[i] == 0:
						subprocess.call('./cli.js on ' + str(i) + '',shell=True)
						state[i] = 1
				else:
					print "apagar relay " + str(i)
					print state[i]
					if state[i] == 1:
						subprocess.call('./cli.js off ' + str(i) + '', shell=True)
						state[i] = 0
			elif "EPA" in configs[i][0]:
				if temp[i] > fermEPA and temp[9] < temp[i]:
					print "encender relay " + str(i)
					print state[i]
					if state[i] == 0:
						subprocess.call('./cli.js on ' + str(i) + '', shell=True)
						state[i] = 1
				else:
					print "apagar relay " + str(i)
					print state[i]
					if state[i] == 1:
						subprocess.call('./cli.js off ' + str(i) + '', shell=True)
						state[i] = 0
			elif "WEISS" in configs[i][0]:
				if temp[i] > fermWEISS and temp[9] < temp[i]:
					subprocess.call('./cli.js on ' + str(i) + '', shell=True)
				else:
					subprocess.call('./cli.js off ' + str(i) + '', shell=True)
			elif "IPA" in configs[i][0]:
				if temp[i] > fermIPA and temp[9] < temp[i]:
					print "encender relay " + str(i)
					print state[i]
					text_file2.write( datetimeWrite + "," + str(temp[i]) + "\n")
					if state[i] == 0:
						subprocess.call('./cli.js on ' + str(i) + '', shell=True)
						state[i] = 1
				else:
					print "apagar relay " + str(i)
					print state[i]
					if state[i] == 1:
�						subprocess.call('./cli.js off ' + str(i) + '', shell = True)
						state[i] = 0
			elif "Porter" in configs[i][0]:
				if temp[i] > fermWEISS and temp[9] < temp[i]:
					print "encender relay " + str(i)
					print state[i]
					if state[i] == 0:
						subprocess.call('./cli.js on ' + str(i) + '', shell = True)
						state[i] = 1
				else:
					print "apagar relay " + str(i)
					print state[i]
					if state[i] == 1:
						subprocess.call('./cli.js off ' + str(i) + '', shell = True)
						state[i] = 0
			elif "Strong" in configs[i][0]:
				if temp[i] > 23 and temp[9] < temp[i]:
					print "encender relay " + str(i)
					text_file.write(datetimeWrite + "," + str(temp[i]) + "\n")
					print state[i]
					if state[i] == 0:
						subprocess.call('./cli.js on ' + str(i) + '', shell = True)
						state[i] = 1
				else:
					print "apagar relay " + str(i)
					text_file.write(datetimeWrite + "," + str(temp[i]) + "\n")
					print state[i]
					if state[i] == 1:
						subprocess.call('./cli.js off ' + str(i) + '', shell = True)
						state[i] = 0
		#Descanso Diacetilo
		elif "diac" in configs[i][1]:
			if temp[i] > diac and temp[9] < temp[i]:
				print "encender relay " + str(i)
				print state[i]
				if state[i] == 0:
					subprocess.call('./cli.js on ' + str(i) + '', shell=True)
					state[i] = 1
			else:
				print "apagar relay " + str(i)
				print state[i]
				if state[i] == 1:
					subprocess.call('./cli.js off ' + str(i) + '', shell=True)
					state[i] = 0
		#Maduracion
		elif "madu" in configs[i][1]:
			if i < 3 or i > 5:
				if temp[i] > madu and temp[9] < temp[i]:
					print "encender relay " + str(i)
					print state[i]
					if state[i] == 0:
						subprocess.call('./cli.js on ' + str(i) + '', shell=True)
						state[i] = 1
				else:
					print "apagar relay " + str(i)
					print state[i]
					if state[i] == 1:
						subprocess.call('./cli.js off ' + str(i) + '', shell=True)
						state[i] = 0
			else:
				if temp[i] > madug and temp[9] < temp[i]:
					print "encender relay " + str(i)
					print state[i]
					if state[i] == 0:
						subprocess.call('./cli.js on ' + str(i) + '', shell=True)
						state[i] = 1
				else:
					print "apagar relay " + str(i)
					print state[i]
					if state[i] == 1:
						subprocess.call('./cli.js off ' + str(i) + '', shell=True)
						state[i] = 0
		#Dry Hop
		elif "dryh" in configs[i][1]:
			if temp[i] > dryh and temp[9] < temp[i]:
				print "encender relay " + str(i)
				print state[i]
				if state[i] == 0:
					subprocess.call('./cli.js on ' + str(i) + '', shell=True)
					state[i] = 1
			else:
				print "apagar relay " + str(i)
				print state[i]
				if state[i] == 1:
					subprocess.call('./cli.js off ' + str(i) + '', shell=True)
					state[i] = 0
		elif "apagado" in configs[i][1]:
			if state[i] == 1:
				subprocess.call('./cli.js off ' + str(i) + '', shell=True)
				state[i] = 0

	#sql1 = ("""INSERT INTO tempLog1 (datetime, temp) VALUES (%s,%s)""",(dateTimeWrite,temp[0]))
	#sql2 = ("""INSERT INTO tempLog2 (datetime, temp) VALUES (%s,%s)""",(dateTimeWrite,temp[1]))
	#sql3 = ("""Insert INTO tempLog3 (datetime, temp) VALUES (%s,%s)""",(dateTimeWrite,temp[2]))

	#try:
		#print "Escribiendo en la BD..."
		#Ejecutando el comando SQL
		#cur.execute(*sql1)
		#cur.execute(*sql2)
		#cur.execute(*sql3)
		#Realizar los cambios en la BD
		#db.commit()
		#print "Completado."
	#except	Exception, e:
		#Retroceder en caso de que algo falle
		#db.rollback()
		#print "Error :" + str(e)
	
	time.sleep(5)
	if cont < 70:
		cont = cont + 1
	else:
		state = [0]*16
		cont = 0
		subprocess.call('./cli.js reset', shell=True) 
