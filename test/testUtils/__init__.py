import ibmiotf.application
import os

class AbstractTest(object):
    WIOTP_API_KEY=os.getenv("WIOTP_API_KEY")
    WIOTP_API_TOKEN=os.getenv("WIOTP_API_TOKEN")
    
    appOptions = {'auth-key': WIOTP_API_KEY, 'auth-token': WIOTP_API_TOKEN}
    setupAppClient = ibmiotf.application.Client(appOptions)
    
    ORG_ID = setupAppClient._options["org"]
    



    
    
