# Import SDK packages
import datetime
import logging
import os
import sys
import threading
import time
import uuid

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from Adafruit_BME280 import *

backlog = {}
killlist = []
threadLock = threading.Lock()
watchdogCounter = 0

# config here
LOG_LEVEL = logging.INFO
CRASH_FILE = 'crash.txt'
WATCHDOG_FILE = 'watchdog.txt'
WATCHDOG_TIME = 60  # seconds
WATCHDOG_LIMIT = 10  # number of watchdog events before software reset
SENSOR_ADDR = 0x76
SEND_BLOCK_SIZE = 25  # how many backlogged items to send in one drop
SAMPLE_INTERVAL = 55  # seconds
MIN_RETRY_TIME = 15  # normal communications interval
MAX_RETRY_TIME = 600  # maximum backoff time

# aws
AWS_CLIENT_ID = 'IoT-1'
AWS_ENDPOINT = 'data.iot.us-west-2.amazonaws.com'
AWS_ENDPOINT_PORT = 8883
AWS_ROOT_CA = 'certs/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem'
AWS_PRIVATE_KEY_PATH = 'certs/05ffb0aef7-private.pem.key'
AWS_CERT_PATH = 'certs/05ffb0aef7-certificate.pem.crt'
AWS_CLIENT_TOPIC = 'sdk/test/java'


# detail exception
def dumpException(source, ex):
    try:
        logging.info(ex)
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.info('Exception: ' + source + ' : ' + message)
    except Exception as ex2:
        logging.info(ex2)


# Suback callback
def customCallback(client, userdata, message):
    try:
        json = str(message.payload.decode("utf-8"))
        callbackuuid = getUuid(json)
        logging.info(
            'Rec customCallback(): ' + message.topic + ' backlog size: ' + str(
                len(backlog)) + ' removing: ' + callbackuuid)
        killlist.append(callbackuuid)
    except Exception as ex:
        dumpException('customCallback()', ex)


# Get uuid from json message
def getUuid(json):
    start = json.find("msgid") + 8
    return json[start:start + 36]


def myOnOnlineCallback():
    logging.debug('online')


def myOnOfflineCallback():
    logging.debug('offline')


def readSensor():
    logging.info('-- start sensor --')
    sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8, address=SENSOR_ADDR)
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
            ).strip()
            with threadLock:
                if len(backlog) > 0:
                    with open(CRASH_FILE, "a") as af:
                        logging.info('Appending')
                        af.write(message + '\n')
                else:
                    with open(CRASH_FILE, "w") as wf:
                        logging.info('Writing')
                        wf.write(message + '\n')
                        if os.path.exists(WATCHDOG_FILE):
                            logging.info('Removing watchdog file - all sent')
                            os.remove(WATCHDOG_FILE)
                backlog[uuid4] = message
                logging.info('Date: ' + str(today) + ' ' + str(now) +
                             ' Add to backlog: ' + str(len(backlog)) + ' : ' + message)
            time.sleep(SAMPLE_INTERVAL)
        except Exception as ex:
            dumpException('readSensor()', ex)


def sender():
    retryTime = MIN_RETRY_TIME
    global watchdogCounter
    logging.info('-- start sender --')
    myMQTTClient = getClient()
    while True:
        try:
            removeSentItems()
            q = getSendQueue()
            try:
                # this can be compacted down considerably.  Code is broken out to
                # try and analyse a connection issue in the underlying library
                logging.info('Send list size: ' + str(len(q)))
                if len(q) > 0:
                    logging.info('Get client')
                    conn = myMQTTClient.connect(120)
                    time.sleep(2)
                    if conn:
                        if myMQTTClient.subscribe(AWS_CLIENT_TOPIC, 1, customCallback):
                            logging.info('Subscribed. Sending: ' + str(len(q)))
                            for key in q:
                                message = q[key]
                                logging.info('Sending: ' + message)
                                try:
                                    myMQTTClient.publish(AWS_CLIENT_TOPIC, message, 0)
                                    time.sleep(0.5)
                                    retryTime = MIN_RETRY_TIME
                                    logging.info('Reset retry time to: ' + str(retryTime))
                                except Exception as ex:
                                    dumpException('sender(1)', ex)
                                    break
                            try:
                                logging.info('Unsubscribe')
                                myMQTTClient.unsubscribe(AWS_CLIENT_TOPIC)
                            except Exception as ex:
                                dumpException('sender(2)', ex)
                        else:
                            logging.info('Unable to subscribe')
                        try:
                            logging.info('Disconnect')
                            myMQTTClient.disconnect()
                        except Exception as ex:
                            dumpException('sender(3)', ex)
                    else:
                        retryTime = retryTime * 2
                        if retryTime > MAX_RETRY_TIME:
                            retryTime = MAX_RETRY_TIME
                        logging.info('Unable to connect. Retry time now: ' + str(retryTime))
                else:
                    logging.info('Queue empty')
            except Exception as ex:
                logging.info('Exception in sender()')
                dumpException('sender(5)', ex)
                try:
                    logging.info('Disconnect tidy up')
                    myMQTTClient.disconnect()
                except Exception as ex:
                    dumpException('sender(5)', ex)
        except Exception as ex:
            logging.info('Exception in sender()')
            dumpException('sender(4)', ex)
        with threadLock:
            watchdogCounter = 0
        time.sleep(retryTime)


# build a queue of items to send
def getSendQueue():
    q = {}
    with threadLock:
        logging.info('Backlog: ' + str(len(backlog)))
        if len(backlog) > 0:
            count = 0
            for key in backlog:
                logging.info('Add: ' + key)
                q[key] = backlog[key]
                count += 1
                if count >= SEND_BLOCK_SIZE:
                    break
    return q


# remove all confirmed sent items
def removeSentItems():
    # remove sent items
    logging.info('Kill list: ' + str(len(killlist)))
    if len(killlist) > 0:
        with threadLock:
            # remove sent items
            while len(killlist) > 0:
                killuuid = killlist[0]
                del (killlist[0])
                del (backlog[killuuid])
                logging.info('Removed: ' + killuuid)


# set up AWS client
def getClient():
    # For certificate based connection
    myMQTTClient = AWSIoTMQTTClient(AWS_CLIENT_ID)
    myMQTTClient.configureEndpoint(AWS_ENDPOINT, AWS_ENDPOINT_PORT)
    myMQTTClient.configureCredentials(AWS_ROOT_CA, AWS_PRIVATE_KEY_PATH, AWS_CERT_PATH)
    #
    myMQTTClient.configureOfflinePublishQueueing(0)  # Disable offline Publish queueing
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    #
    myMQTTClient.onOnline = myOnOnlineCallback
    myMQTTClient.offOnline = myOnOfflineCallback
    return myMQTTClient


# dump all outstanding readings and delete crash recovery file if successful
def dumpCaptures():
    with threadLock:
        f = open(WATCHDOG_FILE, "w")
        for key in backlog:
            logging.info('Saving: ' + key)
            f.write(backlog[key] + '\n')
        if os.path.exists(CRASH_FILE):
            os.remove(CRASH_FILE)


# load data from a file
def fileLoader(file):
    with open(file, "r") as ins:
        for json in ins:
            json = json.strip()
            if len(json) > 20:
                backlog[getUuid(json)] = json
                logging.info('loading: ' + json)


# load outstanding readings to restore state
def loadCaptures():
    logging.info('Load crash file')
    if os.path.exists(CRASH_FILE):
        fileLoader(CRASH_FILE)
    logging.info('Load watchdog file')
    if os.path.exists(WATCHDOG_FILE):
        fileLoader(WATCHDOG_FILE)


def configLogging():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    fh = logging.FileHandler('iot.log')
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)


# system start
configLogging()
loadCaptures()
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
        time.sleep(WATCHDOG_TIME)
        logging.info('watchdog {}'.format(watchdogCounter))
        watchdogCounter += 1
        if watchdogCounter >= WATCHDOG_LIMIT:
            logging.info('Watchdog shutdown')
            dumpCaptures()
            sys.exit(1)
    except KeyboardInterrupt:
        logging.info('Keyboard shutdown')
        dumpCaptures()
        sys.exit(0)
