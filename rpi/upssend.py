#!/usr/bin/python3
import adafruit_bme280
import board
import busio
import datetime
import digitalio
import time
import time
import uuid
from pijuice import PiJuice  # Import pijuice module


def fixJson(bad):
    val = str(bad).replace("'", "\"").replace("True", "true").replace("False", "false")
    return val


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


def getTimestamp():
    today = datetime.date.today()
    calday = today.strftime("%d") + '-' + today.strftime("%m") + '-' + today.strftime("%Y")
    now = datetime.datetime.now().time()
    minute = now.hour * 60 + now.minute
    return '''"caldate":"{date}","calminute": {minute}'''.format(date=calday, minute=minute)


# Instantiate PiJuice interface object
pijuice = PiJuice(1, 0x14)

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25

while True:
    status = fixJson(pijuice.status.GetStatus())
    charge = fixJson(pijuice.status.GetChargeLevel())
    fault = fixJson(pijuice.status.GetFaultStatus())
    timestamp = getTimestamp()

    json = "{ \"api\":\"2\",\"msgid\": \"" + str(uuid.uuid4()) + "\"," + timestamp + ", \"sensor\": " + readSensor(
        bme280) + ", \"status\": " + status + ", \"charge\": " + charge + ", \"fault\": " + fault + " }"

    print(json)

    time.sleep(5)
