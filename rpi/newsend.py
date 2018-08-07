# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.core.util.enums import DropBehaviorTypes

from Adafruit_BME280 import *
import sys
import time
import datetime
import uuid
import logging
import threading
import queue

backlog = {}
killlist = []
threadLock = threading.Lock()


# Suback callback
def customSubackCallback(mid, data):
    print('Received SUBACK packet id: ', mid, ' Granted QoS: ', data)


def dumpException(source, ex):
    try:
        logging.debug(ex)
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print('Exception: ', source, message)
    except Exception as ex2:
        print(ex)
        print(ex2)


# Suback callback
def customCallback(client, userdata, message):
    try:
        json = str(message.payload.decode("utf-8"))
        start = json.find("msgid") + 8
        uuid = json[start:start + 36]
        #
        print('Received customSubackCallback(): ', uuid, message.topic, 'backlog size; ', len(backlog), 'removing: ',
              uuid)
        #
        killlist.append(uuid)
    except Exception as ex:
        dumpException('customCallback()', ex)


def myOnOnlineCallback():
    logging.debug('** online **')


def myOnOfflineCallback():
    logging.debug('** offline **')


def readSensor():
    print('-- start sensor --')
    while True:
        try:
            today = datetime.date.today()
            calday = today.strftime("%d") + '-' + today.strftime("%m") + '-' + today.strftime("%Y")
            now = datetime.datetime.now().time()
            minute = now.hour * 60 + now.minute
            #
            degrees = sensor.read_temperature()
            pressure = sensor.read_pressure() / 100
            humidity = sensor.read_humidity()
            #
            uuid4 = str(uuid.uuid4())
            message = '''
            {{"msgid":"{uuid}","caldate":"{date}","calminute": {minute},"pitemp0": "{t0:.2f}","pihum0": "{h0:.2f}","pipress0": "{p0:.2f}"}}
            '''.format(
                uuid=uuid4,
                date=calday,
                minute=minute,
                t0=degrees,
                h0=humidity,
                p0=pressure
            )
            with threadLock:
                backlog[uuid4] = message.strip()
                print('Read date: ' + str(today) + ' ' + str(now), 'Adding item to backlog: ', len(backlog))
            time.sleep(45)
        except Exception as ex:
            dumpException('readSensor()', ex)


def sender():
    print('-- start sender --')
    #
    # For certificate based connection
    myMQTTClient = AWSIoTMQTTClient("xyzzy")
    myMQTTClient.configureEndpoint("data.iot.us-west-2.amazonaws.com", 8883)
    myMQTTClient.configureCredentials("certs/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem",
                                      "certs/05ffb0aef7-private.pem.key", "certs/05ffb0aef7-certificate.pem.crt")
    #
    myMQTTClient.configureOfflinePublishQueueing(0)  # Disable offline Publish queueing
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    #
    myMQTTClient.onOnline = myOnOnlineCallback
    myMQTTClient.offOnline = myOnOfflineCallback
    #
    while True:
        try:
            # remove sent items
            print('Kill list size: ', len(killlist))
            if len(killlist) > 0:
                with threadLock:
                    # remove sent items
                    while len(killlist) > 0:
                        uuid = killlist[0]
                        del (killlist[0])
                        del (backlog[uuid])
                        print('Kill remove: ', uuid)
            # get next items to send
            print('Backlog list size: ', len(backlog))
            q = {}
            if len(backlog) > 0:
                with threadLock:
                    count = 0
                    for key in backlog:
                        print('Adding to queue: ', key)
                        q[key] = backlog[key]
                        count = count + 1
                        if count >= 25:
                            break
            #
            print('Send list size: ', len(q))
            if len(q) > 0:
                print('Get connection and send items')
                conn = myMQTTClient.connect(60)
                print('Connection made ?', conn)
                if conn:
                    if myMQTTClient.subscribe("sdk/test/java", 1, customCallback):
                        print('Subscribed. Attempting to send records: ', len(q))
                        for key in q:
                            message = q[key]
                            print('Sending: ', message)
                            try:
                                myMQTTClient.publish("sdk/test/java", message, 0)
                                time.sleep(1)
                            except Exception as ex:
                                dumpException('sender(1)', ex)
                                break
                        try:
                            print('Unsubscribe')
                            myMQTTClient.unsubscribe("sdk/test/java")
                        except Exception as ex:
                            dumpException('sender(2)', ex)
                    else:
                        print('Unable to subscribe')  #
                    try:
                        print('Disconnect')
                        myMQTTClient.disconnect()
                    except Exception as ex:
                        dumpException('sender(3)', ex)
                else:
                    print('Unable to connect')
            else:
                print('No queued data available to send')
        except Exception as ex:
            dumpException('sender(4)', ex)
        time.sleep(30)


# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
# logging.basicConfig(filename='iot.log', level=logging.INFO)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
#
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8, address=0x76)
#
time.sleep(2)
#
tReadSensor = threading.Thread(target=readSensor)
tReadSensor.setDaemon(True)
tReadSensor.start()
#
tSender = threading.Thread(target=sender)
tSender.setDaemon(True)
tSender.start()

while True:
    try:
        time.sleep(60)
        print('tick')
    except KeyboardInterrupt:
        sys.exit()
