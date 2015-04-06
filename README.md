# omxAutomation
Tools to operate omxplayer nicely from remote

Stefan Koch <StefanKoch@gmx.org>

Install:
1. have omxplayer working on Raspberry PI

2. install python2

3. install python modules if needed (see source code)

4. have mosquitto running, no TLS support at the moment
	e.g. I use a local instance

5. add omxserver.py to startup (you should run it as regular user)
	e.g. su -c /somepath/omxserver.py <regular user> &

6. adjust install path in python scripts

7. ajdust media path in vid* scripts

5. copy vid* scripts to cgi-bin path of your web-browser

6. you should be able to browse and play using
	e.g. http://<your ip>/cgi-bin/vidlist


Known Issues
1 - no language file - you need to adapt your language in source code
2 - slow response on button control due simple cgi invocation
