import socket
import os
import smtplib
from email.mime.text import MIMEText
import traceback
import json
        
# Raise a PagerDuty event (or just send an email) using the key (subject) and message (body) arguments.
def raiseEvent(key, message):
	try:
		pagerDutyEmail = os.getenv('pagerdutyemail', None)		
		smtpServer = None
		smtpUsername = None
		smtpPassword = None
		fromField = None
		
		# get SendGrid username/password from VCAP if available
		if "VCAP_APPLICATION" in os.environ:
			application = json.loads(os.getenv('VCAP_APPLICATION'))
			# get app name to set From field
			fromField = application['application_name'] + "@mybluemix.net"
			
			service = json.loads(os.getenv('VCAP_SERVICES'))
			# Check if we have a SendGrid service bound
			if "sendgrid" in service:
				print(" SendGrid service has been bound.")
				smtpServer = service['sendgrid'][0]['credentials']['hostname']
				smtpUsername = service['sendgrid'][0]['credentials']['username']
				smtpPassword = service['sendgrid'][0]['credentials']['password']
		
		# otherwise get smtp details from env
		if smtpServer is None:
			smtpServer = os.getenv('smtpserver', None)
			smtpUsername = os.getenv('smtpusername', None)
			smtpPassword = os.getenv('smtppassword', None)
		
		if fromField is None:
			fromField = socket.gethostname() + "@bluemix.net"
		
		# send email if we have enough details
		if pagerDutyEmail is not None and smtpServer is not None:
			print(" Triggering PagerDuty event with \"" + key + "\" and message \"" + message + "\"")
			msg = MIMEText(message)
			msg["Subject"] = "%s" % (key)
			msg["From"] = fromField
			msg["To"] = pagerDutyEmail
			
			s = smtplib.SMTP(smtpServer)
			s.login(smtpUsername,smtpPassword)
			s.sendmail(fromField, [pagerDutyEmail], msg.as_string())
			print(" Sent email to %s" % pagerDutyEmail)
			s.quit()
			
		else:
			print(" No PagerDuty email or SMTP server found in environment.  Event message would have been \"" + key + "\" and message \"" + message + "\"")
			
	except Exception as e:
		print(" Exception occurred attempting to send email to PagerDuty: %s %s" % (str(e), traceback.format_exc()))
