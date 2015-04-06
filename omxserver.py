#!/usr/bin/python
########################################################################################
#
# Copyright by Stefan Koch <StefanKoch@gmx.org>, 2015
#
# This file is part of omxAutomation
#
#    omxAutomation is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    omxAutomation is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################################

import paho.mqtt.client as mqtt
import subprocess
import time
import signal
import sys

#######################################################################################
#Defines you need to adapt
install_path     = "/home/stefan/bin"
mqtt_broker_ip   = "192.168.2.100"
mqtt_broker_port = "1883"
mqtt_omx_topic   = "/omxserver/play"

#######################################################################################
omxproc = subprocess.Popen
playing = 0
run = True

def sigint_handler(signal, frame):
	global run
	print("OMXServer will terminate (SIGINT)")
	run = False

def play_quit():
	global playing
	if (playing == 1):
		print("QUIT PLAY, wait for termination")
		omxproc.stdin.write('q')
		while omxproc.poll() is None:
			time.sleep(0.5)
		print("Player has ended")
		playing = 0

def start_play(url):
	global playing
	global omxproc
	print url
	if (playing == 1):
		play_quit()
	playing = 1
	print("play "+url)
	omxproc = subprocess.Popen(['/usr/bin/omxplayer', 
			      '--key-config', install_path+'/omxkeys.txt', 
			      '--win', '1 1 1920 1080', 
			      '-o','local', 
			      url],stdout=subprocess.PIPE,stdin=subprocess.PIPE)

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

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe(mqtt_omx_topic)

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
		print("cmd="+cmd+" arg="+arg)
		dispatch_message(cmd, arg)

#######################################################################################
print("OMXPLAYER Server")
signal.signal(signal.SIGINT, sigint_handler)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker_ip, mqtt_broker_port, 60)

while run:
	client.loop()

#fixme shutdown not as clean as desired now (hardcoded time)
print("player shuddown")
if (playing == 1):
	omxproc.stdin.write('q')
	time.sleep(2)
	playing = 0
