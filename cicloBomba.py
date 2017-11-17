import os
import subprocess
import sys
import glob
import time
from time import strftime

while True:
	#apagar bomba estanques (rele 16)
	subprocess.call('./cli.js on 15', shell=True)
	print "Bomba Apagada"
	time.sleep(600)
	#encender bomba estanques (rele 16)
	subprocess.call('./cli.js off 15', shell=True)
	print "Bomba Encendida"
	time.sleep(3000)
