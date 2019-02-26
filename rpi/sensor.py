#!/usr/bin/python3
import datetime
import logging
import os
import threading
import time
import uuid

import adafruit_bme280
import board
import busio
from pijuice import PiJuice

# config here
LOG_LEVEL = logging.INFO
EVENT_FILE = 'event.txt'
CRASH_FILE = 'crash.txt'
SENSOR_ADDR = 0x76
SEND_BLOCK_SIZE = 25  # how many backlogged items to send in one drop
SAMPLE_INTERVAL = 55  # seconds
MIN_RETRY_TIME = 15  # normal communications interval
MAX_RETRY_TIME = 600  # maximum backoff time

#
# Utility methods
#

def dumpException(source, ex):
    try:
        logging.info(ex)
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.info('Exception: ' + source + ' : ' + message)
    except Exception as ex2:
        logging.info(ex2)

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

# Get uuid from json message
def getUuid(json):
    start = json.find("msgid") + 8
    return json[start:start + 36]

def getTimestamp():
    today = datetime.date.today()
    calday = today.strftime("%d") + '-' + today.strftime("%m") + '-' + today.strftime("%Y")
    now = datetime.datetime.now().time()
    minute = now.hour * 60 + now.minute
    return '''"caldate":"{date}","calminute": {minute}'''.format(date=calday, minute=minute)

#
# File handling
#

# dump all outstanding readings
def dumpCaptures():
    if os.path.exists(CRASH_FILE):
        os.remove(CRASH_FILE)
    f = open(CRASH_FILE, "w")
    for key in backlog:
        logging.info('Saving: ' + key)
        f.write(backlog[key] + '\n')
    f.close()
    if os.path.exists(EVENT_FILE):
        os.remove(EVENT_FILE)
    if os.path.exists(CRASH_FILE):
        os.rename(CRASH_FILE, EVENT_FILE)

# load data from a file
def fileLoader(file):
    if os.path.exists(file):
        with open(file, "r") as ins:
            for json in ins:
                json = json.strip()
                if len(json) > 20:
                    backlog[getUuid(json)] = json
                    logging.info('loading: ' + json)
    return backlog

def saveMessage(json, uuid4):
    if len(backlog) > 0:
        with open(EVENT_FILE, "a") as af:
            logging.info('Appending ' + json)
            af.write(json + '\n')
    else:
        with open(EVENT_FILE, "w") as wf:
            logging.info('Writing ' + json)
            wf.write(json + '\n')
    backlog[uuid4] = json
    print('-- record saved --')

def loadFiles():
    fileLoader(EVENT_FILE)
    fileLoader(CRASH_FILE)
    print('{size} records loaded from backlog'.format(size=len(backlog)))

#
# rpi
#

def powerManagement():
    print('Power management')

#
# piJuice
#

def fixJson(bad):
    val = str(bad).replace("'", "\"").replace("True", "true").replace("False", "false")
    return val

def getPiJuice():
    return PiJuice(1, 0x14)

#
# BME280
#
def readSensor(sensor):
    degrees = sensor.temperature
    humidity = sensor.humidity
    pressure = sensor.pressure

    message = '''
    {{"pitemp0": "{t0:.2f}","pihum0": "{h0:.2f}","pipress0": "{p0:.2f}"}}
    '''.format(
        t0=degrees,
        h0=humidity,
        p0=pressure
    ).strip()
    return message

def getBME280():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    # change this to match the location's pressure (hPa) at sea level
    bme280.sea_level_pressure = 1013.25
    return bme280

def getSensorMessage(piJuice, bme280, uuid4):
    status = fixJson(piJuice.status.GetStatus())
    charge = fixJson(piJuice.status.GetChargeLevel())
    fault = fixJson(piJuice.status.GetFaultStatus())
    timestamp = getTimestamp()

    return "{ \"api\":\"2\",\"msgid\": \"" + uuid4 + "\"," + timestamp + ", \"sensor\": " + readSensor(
        bme280) + ", \"status\": " + status + ", \"charge\": " + charge + ", \"fault\": " + fault + " }"

#
# amazon iot
#
def sender():
    print('-- sender {s}--'.format(s=len(backlog)))

#
# Main()
#
try:
    time.sleep(5)
    configLogging()
    print('get data')
    backlog = {}
    loadFiles()
    uuid4 = str(uuid.uuid4())
    json = getSensorMessage(getPiJuice(), getBME280(), uuid4)
    saveMessage(json, uuid4)
    print(json)
    #
    dumpCaptures()
    #
    # Try to send data
    tSender = threading.Thread(target=sender)
    tSender.setDaemon(True)
    tSender.start()
    #
    time.sleep(5)
except Exception as ex:
    dumpException('main', ex)
finally:
    print('-- shutdown --')
