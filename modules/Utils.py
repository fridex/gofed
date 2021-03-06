from subprocess import PIPE
from subprocess import Popen
import os

RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
WHITE = '\033[97m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
GREY = '\033[90m'
BLACK = '\033[90m'
DEFAULT = '\033[99m'
ENDC = '\033[0m'

def runCommand(cmd):
	#cmd = cmd.split(' ')
	process = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
	stdout, stderr = process.communicate()
	rt = process.returncode

	return stdout, stderr, rt

def getScriptDir():
	return os.path.dirname(os.path.realpath(__file__))

def inverseMap(mfnc):
	"""inverse mapping of multifunction

	Keyword arguments:
	mfnc -- multifunction
	"""
	imap = {}
	for key in mfnc:
		for image in mfnc[key]:
			if image not in imap:
				imap[image] = [key]
			else:
				imap[image].append(key)
	return imap

