#!/bin/sh

while true
do
    if [ ! $(pidof -x cam_capture.py) ]
    then
	echo "cam_capture not running"
	# Start main application
        /home/indyme/cam_cap/cam_capture.py > /home/indyme/cam_cap/cam_cap.log 2>&1 &
    fi

    if [ ! $(pidof -x webserver.js) ]
    then
	echo "Web server not running"
	 /home/indyme/cam_cap/webserver.js > /home/indyme/cam_cap/web.log 2>&1 &
    fi
    sleep 1
done
