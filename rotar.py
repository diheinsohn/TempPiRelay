import os
import subprocess
import datetime
import time
import glob
import signal
import sys
from time import strftime
from subprocess import STDOUT, check_output
while True:
	p = check_output('python readTempPi.py',stderr=STDOUT, timeout=30)
	print "pausa"
	subprocess.call('./cli.js reset', shell = True)
	time.sleep(60*10)
