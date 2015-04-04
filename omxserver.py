#!/usr/bin/python

import paho.mqtt.client as mqtt
import subprocess
import time
import signal
import sys

#######################################################################################
omxproc = subprocess.Popen
playing = 0
run = True

def sigint_handler(signal, frame):
	global run
	print("OMXServer will terminate (SIGINT)")
	run = False

def start_play(url):
	global playing
	global omxproc
	if (playing == 0):
		print("play "+url)
		omxproc = subprocess.Popen(['/usr/bin/omxplayer', 
				      '--key-config', '/home/stefan/bin/omxkeys.txt', 
				      '--win', '1 1 1920 1080', 
				      '-o','hdmi', 
				      url],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
	#if (omxproc.returncode >= 0):
	playing = 1

def seek_fwd():
	if (playing == 1):
		print("SEEK FWD")
		omxproc.stdin.write('r')

def seek_back():
	if (playing == 1):
		print("SEEK BACK")
		omxproc.stdin.write('l')

def play_pause():
	if (playing == 1):
		print("PLAY/PAUSE")
		omxproc.stdin.write(' ')

def play_quit():
	global playing
	if (playing == 1):
		print("QUIT PLAY, wait for termination")
		omxproc.stdin.write('q')
		while omxproc.poll() is None:
			time.sleep(0.5)
		print("Player has ended")
		playing = 0

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("/omxserver/play")

def dispatch_message(cmd, arg):
	if (cmd == 'play'):
		start_play(arg)
		return
	if (cmd == 'fwd'):
		seek_fwd()
		return
	if (cmd == 'back'):
		seek_back()
		return
	if (cmd == 'playpause'):
		play_pause()
		return
	if (cmd == 'quit'):
		play_quit()

def on_message(client, userdata, msg):
	#print(msg.topic+" "+str(msg.payload))
	message = msg.payload.split(",")
	if (len(message) == 2):
		cmd = message[0]
		arg = message[1]
		#print("cmd="+cmd+" arg="+arg)
		dispatch_message(cmd, arg)

#######################################################################################
print("OMXPLAYER Server")
signal.signal(signal.SIGINT, sigint_handler)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.100", 1883, 60)
#client.loop_forever()

while run:
	client.loop()

print("player shuddown")
if (playing == 1):
	omxproc.stdin.write('q')
	time.sleep(2)
	playing = 0
