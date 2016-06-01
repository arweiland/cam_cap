#!/usr/bin/python

# First attempt to keep a circular buffer and write .jpg file while recording.
# This version records 10 seconds in buffer.  It writes the jpeg when it receives
# a SIGINT2, waits trigger_delay period, then save the h.264 file.
#
# Ron Weiland, 09/21/15


import io
import picamera
import signal
import subprocess
import datetime
import os
from send_gmail import send_gmail
import sys
import traceback

trigger_delay = 3            # How long after trigger before writing video
video_length = 10            # How long to record video

write_now = False
exit_now = False

# Get path we are running from.  Not current directory if started from script
ourpath = os.path.dirname(os.path.abspath(__file__)) + '/'

sys.path.append( ourpath[:-1] )         # Add current directory to search path for modules


image_file = ourpath + 'public/foo.jpg'
small_image_file = ourpath + 'public/foo_small.jpg'
video_file = ourpath + 'public/foo.h264'
mp4_file = ourpath + 'public/foo.mp4'
email_file = ourpath + 'email.html'

def write_image():
    # use_video_port = True to keep the camera from having to change modes
    camera.capture(image_file, use_video_port=True)
    print "Wrote Image"

def downsize_image():
    print "Downsizing image"
    cmd = ["convert", image_file, "-resize", "220", small_image_file]
    subprocess.call( cmd )
    print "Convert returned"

def wrap_video():
# MP4Box -fps x -add <video_file> -new <output_file.mp4>
    print "Containerizing video file"
    cmd = ["MP4Box", "-fps", "30", "-add", video_file, "-new", mp4_file]
    ret = subprocess.call( cmd )
    print "MP4Box returned"

def write_video( stream ):
    print "Started writing file"
    with stream.lock:               # (in case we haven't stopped recording)
        # Find the first header frame in video
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break

        with io.open( video_file, 'wb' ) as output:
            output.write(stream.read())

    # Wipe the circular stream once we are done
    print "Ended writing file"
    stream.seek(0)
    stream.truncate()


# This handler is entered when the program receives a SIGUSR1 signal
def signal_handler( signal, frame ):
    global write_now
    print "Got signal!"
    write_now = True

# This handler shouldn't be entered at all
def signal_handler2( signal, frame ):
    print "Got signal 2!"
    
# This handler is entered when the program receives a SIGINT signal (^c)
def exit_handler( signal, frame ):
    global exit_now
    print "Got exit signal!"
    exit_now = True

# Register the signal handler
signal.signal(signal.SIGUSR1, signal_handler)

# Register the signal handler
signal.signal(signal.SIGUSR2, signal_handler2)

# Register the exit handler
signal.signal(signal.SIGINT | signal.SIGTERM, exit_handler)

# Start the camera
with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.bitrate = 17000000
#    camera.bitrate =  5000000
#    camera.framerate = 10

    #Calculate the seconds based on resoution (at 30 fps)
    image_sec = 10                 # time in seconds
    secs = int((camera.resolution[0] * camera.resolution[1] * image_sec) / (1920 * 1080))

    # Note: PiCameraCircularIO calcuates buffer as: size = bitrate * seconds // 8

    print "Seconds = ", secs
#    bsize = (camera.bitrate * 10) / 8
    print "Size = ", camera.bitrate * secs // 8
    print "Resolution: ", camera.resolution, "Frame rate: ", camera.framerate
#    stream = picamera.PiCameraCircularIO(camera, seconds=secs )

    bsize = 850000 * video_length
    stream = picamera.PiCameraCircularIO(camera, size = bsize )
    camera.start_recording(stream, format='h264')

    camera.start_preview()
    camera.preview_fullscreen = True
    
    try:
        print "%s Camera capture started" % (datetime.datetime.now())
        while 1:
            camera.wait_recording(.1)
            if write_now:
                write_image();                             # Write the jpg image
                camera.wait_recording( trigger_delay )     # Wait delay period
                camera.stop_recording()                    # Stop the recording
                write_video( stream );                     # Save the video capture
                wrap_video();                              # wrap it in an MP4 container
                downsize_image();                          # downsize the jpg image
#                send_gmail( "email.html", "Alert from CLX", "public/foo_small.jpg" );  # Send out the mail
                send_gmail( email_file, ourpath + "public/foo_small.jpg" );  # Send out the mail               
                print "Restarting video"
                camera.start_recording(stream, format='h264')                
                write_now = False
            if exit_now:
                break
    except Exception as ex:
        print "Exception!!! ", ex

        errfile = open( "cam_cap.log", "w" )
        traceback.print_tb( errfile )

    finally:
        print "Stopped camera"
        camera.stop_recording()

