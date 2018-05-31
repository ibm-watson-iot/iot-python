import ibmiotf.application
import os

class AbstractTest(object):

    WIOTP_API_KEY=os.getenv("WIOTP_API_KEY")
    WIOTP_API_TOKEN=os.getenv("WIOTP_API_TOKEN")
    ORG_ID = os.getenv("WIOTP_ORG_ID")
    
    if WIOTP_API_KEY is None:
        raise Exception("WIOTP_API_KEY environment variable is not set")
    if WIOTP_API_TOKEN is None:
        raise Exception("WIOTP_API_TOKEN environment variable is not set")
    if ORG_ID is None:
        raise Exception("WIOTP_ORG_ID environment variable is not set")
    
    appOptions = {'auth-key': WIOTP_API_KEY, 'auth-token': WIOTP_API_TOKEN}
    setupAppClient = ibmiotf.application.Client(appOptions)
