from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
# from heartbeat import read_pulse, read_temp
from datetime import datetime
import logging
import time
import smbus
import json
import linecache
import argparse


def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("Temperature: " + str(payloadDict["state"]["desired"]["temperature"]))
        print("Pulse: " + str(payloadDict["state"]["desired"]["pulse"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def customShadowCallback_Delete(payload, responseStatus, token):

     # Display status and data from delete request
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")       


def configureLogging():

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


# host = "a2xz6bh1uzu45m-ats.iot.us-west-2.amazonaws.com"
# certPath = "/home/pi/certs_east/certs_true/"
# clientId = "masterproject"
# thingName = "masterproject"
certPath = "/home/pi/certs_east/"
host = "a1ii3qlfr1qukw-ats.iot.us-east-1.amazonaws.com"
clientId = "iot295b_thing"
topic = "iot/temperature"
thingName = "iot295b_thing"

filename = "/home/pi/iotproject/aws-iot-device-sdk-python/cmpe295/pulse_reading.txt"
filename2 = "/home/pi/iotproject/aws-iot-device-sdk-python/cmpe295/temp_reading.txt"

myAWSIoTMQTTShadowClient = None
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials("{}Amazon-root-CA-1.pem".format(certPath), "{}private.pem.key".format(certPath), "{}device.pem.crt".format(certPath))

myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10) 
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)


myAWSIoTMQTTShadowClient.connect()

deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)

deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

loopCount = 0
while True:
    f = open(filename, "r")
    line1 = f.readline()
    f = open(filename2, "r")
    line2 = f.readline()
    temperature_reading = line2
    pulse_reading = line1
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    JSONPayload = '{"state":{"desired":{"time":"' + str(timestamp) + '","temperature":'+ str(temperature_reading) + ',"pulse":' +str(pulse_reading) +'}}}'
    print("\n", JSONPayload,"\n")
    deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 5)
    loopCount += 1
    time.sleep(1)


