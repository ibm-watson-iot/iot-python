import json
import requests
import os

# post data to slack webhook
def postToSlack(data):
	
	try:
		slackURL = os.getenv('slackwebhookurl', None)
		
		if slackURL is not None:
			print(" Posting to slack.")
			r = requests.post(slackURL, json.dumps(data), timeout=5)
			if r.status_code != 200:
				print("Unexpected return code when posting to slack: %s" % (r.status_code))
		else:
			print(" No slack URL found in environment.  Message would have been: %s" % json.dumps(data))
	except Exception as e:
		print(" Exception occurred posting to slack:")
		print(str(e))
