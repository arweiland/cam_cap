#!/usr/bin/python

# This is a CLX module for sending an email alert when the camera module is triggered.
# It sends an email with a jpg attachment along with an HTML image and link back to the captured video
#
#  Ron Weiland, 11/12/15

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib


import os
import sys
import configs

email_str = ''
our_ip = ''
config = {}


# Get path we are running from.  Not current directory if started from script
ourpath = os.path.dirname(os.path.abspath(__file__)) + '/'


# Read configuration file upon module load

def read_config():
   global config
   config = configs.read_config( ourpath + "email.json" )
   if ( config ):
      print "Email Config read"

def get_our_ip():
   global our_ip
   import socket
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.connect(('8.8.8.8', 80))           # Connect to Google's DNS
   our_ip = s.getsockname()[0]
   s.close()
   print "Our IP: ", our_ip

def read_email_template( fname ):
   global email_str
   from string import Template

   # If we don't have our IP yet, get it now
   if not our_ip:
      get_our_ip()
      
   with open( fname, "r" ) as email:
      text = email.read()
      s = Template( text )
      # Substitute our IP address and the web server port into email template
      print "IP: %s, port: %s" % (our_ip, config["link_port"])
      email_str = s.substitute( ip_addr=our_ip, 
                                port=config["link_port"], 
                                location=config["location"] )

def mail(to, subject, text, attach):
   msg = MIMEMultipart('related')           # Note: 'related'
   msg['Subject'] = subject
   msg['From'] = config["gmail_user"]
   msg['To'] = to
   msg.preamble = 'This is a multi-part message in MIME format.'


   # Encapsulate the plain and HTML versions of the message body in an

   # 'alternative' part, so message agents can decide which they want to display.

   msgAlternative = MIMEMultipart('alternative')
   msg.attach(msgAlternative)

   msgText = MIMEText('This is an alternative plain text message.')
   msgAlternative.attach(msgText)

   # Attach the HTML from the file

   msgText = MIMEText( text, 'html' )
   msgAlternative.attach(msgText)

   # msg.attach(MIMEText(text, 'html'))          # attach message as HTML

   # Read in the attachment
   fp = open(attach, 'rb')
   msgImage = MIMEImage(fp.read())
   fp.close()

   # Define the image's ID as referenced in the HTML

   msgImage.add_header('Content-ID', '<image1>')
   msg.attach(msgImage)


   # Encode the attachment
#   if attach:
#      part = MIMEBase('application', 'octet-stream')
#      part.set_payload(open(attach, 'rb').read())
#      Encoders.encode_base64(part)
#      part.add_header('Content-Disposition',
#                      'attachment; filename="%s"' % os.path.basename(attach))
#      msg.attach(part)

   try:
      mailServer = smtplib.SMTP("smtp.gmail.com", 587)
      mailServer.ehlo()
      mailServer.starttls()
      mailServer.ehlo()
   except SMTPConnectError as e:
      print "SMTP failed: ", e

   mailServer.login(config["gmail_user"], config["gmail_pwd"])
   mailServer.sendmail(config["gmail_user"], to.split(','), msg.as_string())

   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

def send_gmail( template, attachment=None ):
   read_email_template( template )
   mail(config["addresses"], config["subject"], email_str, attachment )


#mail("some.person@some.address.com",
#   "Hello from python!",
#   "This is a email sent with python",
#   "my_picture.jpg")

read_config()              # Read the configuration file
#get_our_ip()               # Get our IP address (for email links)

if __name__ == "__main__":
   if len( sys.argv ) < 3:
      print "Please give name of email file to send and image to attach"
      sys.exit(-1)

   send_gmail( sys.argv[1], sys.argv[2] )

else:
   print "Email module initialized"
