import ibmiotf.application
import os

class AbstractTest(object):

    WIOTP_API_KEY=os.getenv("WIOTP_API_KEY")
    WIOTP_API_TOKEN=os.getenv("WIOTP_API_TOKEN")
    ORG_ID = os.getenv("WIOTP_ORG_ID")
    
    appOptions = {'auth-key': WIOTP_API_KEY, 'auth-token': WIOTP_API_TOKEN}
    setupAppClient = ibmiotf.application.Client(appOptions)
