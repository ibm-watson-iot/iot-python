FROM python:3.8-alpine3.11

# Add the required dependencies to install psutil that are missing from alpine
# See: https://github.com/giampaolo/psutil/issues/872#issuecomment-272248943
RUN apk add gcc linux-headers libc-dev

# Begin the install proper
RUN pip install wiotp-sdk==0.10.0 psutil
ADD src/ /opt/ibm/iotpsutil/
RUN chmod +x /opt/ibm/iotpsutil/*.py

ENTRYPOINT ["python", "/opt/ibm/iotpsutil/iotpsutil.py"]
