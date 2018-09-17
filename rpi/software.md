# Software

The software is a Python 3 script which has the following features:

* Interface to the BME280 sensor via I2C
* Write capability to AWS IoT
* Transmission backoff when WiFi is unavailable
* Logging of all readings in filestore until receipt at AWS confirmed to prevent data loss
* Crash recovery of unwritten data
* Restart watchdog for software failure
* Selectable sampling rate
* Selectable write rate

## BME280 Interface

The BME280 is accessed via a library available from Adafruit and hosted on [GitHub](https://github.com/adafruit/Adafruit_Python_BME280).

**Note 1:** The library was deprecated just as the project was completed.  Changing the script to use the latest library is left as an exercise for the reader ...

**Note 2:** To use this library you will also need to install the Adafruit Python GPIO package on [GitHub](https://github.com/adafruit/Adafruit_Python_GPIO)

The software works correctly with Python 3, but some of the examples require tweaking if you want to use them

## AWS IoT Interface

The AWS IoT system is accessed via a library from Amazon and hosted on [GitHub](https://github.com/aws/aws-iot-device-sdk-python)

The site contains comprehensive documentation and details on how to use MQTT.

**Warning**

While using the library, it was found that attempting to make a connection would occasionally fail in a non-recoverable manner.  A call to the library would fail to return and 
would not timeout.  A work around was implemented by putting the MQTT connection code in a thread, and if a lack of activity is detected, restarting the application.

## Backoff

A simple backoff algorithm was implemented to reduce needless processing when WiFi connectivity was not available.  

After each failure, the delay before retrying is doubled, up to a defined maximum (`MAX_RETRY_TIME`).  If a sucessful connection is made, the delay is reset back to the minimum (`MIN_RETRY_TIME`)


## Data Logging & Recovery

As each sample is read, the values are written to the `CRASH_FILE` file.  The contents of the file are read into memory on restart, ready to be transmitted.  The file 
is deleted when the software has sucessfully sent all available reading (i.e. a crash at this point would not lead to data loss).

A second data file exists, `WATCHDOG_FILE`.  This file is used to hold readings not yet sent when a controlled shutdown is performed.  In this instance, the `CRASH_FILE` would be deleted once
all data had been written.  The contents of the file are read into memory on restart, ready to be transmitted.  This file should be considerably smaller than the `CRASH_FILE`, which contains
a record of all data, instead of just those guaranteed not have been written.

This area could be improved by use of a single data store allowing for persistence and dynamic removal of processed records.  However, the dual file system is simple and has 
proven to be reliable in use.

## Sampling / Write Rates

The sensor read operation is implemented as a thread which sleeps between operations.  The time between reads is set in `SAMPLE_INTERVAL`.  It is recommended that the value is set
to a slightly lower value than required. For example, if a one minute sample time is required, set this to 55 seconds.  This will give slightly more readings but will guarantee a 
reading at least every minute.  

The sensor write operation is implemented as a thread which sleeps between operations.  The minimum time between writes is set in `MIN_RETRY_TIME`.  One write operation
can send a block of data, with the maximum number of reads being sent set by `SEND_BLOCK_SIZE`.  This allows the Raspberry Pi to catch up on a backlog when WiFi is restored without consuming 
all available processing resources.

## Watchdog

A simple watchdog is implemented to recover from issues in the sensor read thread.  A counter is incremented every `WATCHDOG_TIME` seconds.  This is reset on every loop of the
read sensor thread.  If it is not reset after `WATCHDOG_LIMIT` iterations, the software dumps all data to  `WATCHDOG_FILE` and halts with a 
system exit code of 1.

An enclosing script, if it detects the status code will restart the program.

```
#!/bin/bash
#
# restart loop until process terminates with state 0
# this is used to stop in a controlled manner, ctrl-c into the python process
#
until python3 newsend.py; do
    echo "IoT watchdog timeout - restart." >&2
    sleep 1
done
```

**Note:** If a keyboard interrupt is used (CTRL-C), then a controlled halt is also performed, but the script does not restart the program.

## Script Configuration

The script being used is [here](newsend.py). The script contains a number of parameters than can be modified to change behaviour.

This is *very* subject to change.

### Script Operation

| Config Item | Default Value | Description |
|:-----|:-----|:-----|
| LOG_LEVEL | logging.INFO | Logging level - useful for debug  |
| CRASH_FILE | 'crash.txt' | File where all unconfirmed sensor readings are stored  |
| WATCHDOG_FILE | 'watchdog.txt' | File where unconfirmed sensor readings are stored in controlled shutdown  |
| WATCHDOG_TIME  | 60 | Time (in seconds) for each watchdog tick  |
| WATCHDOG_LIMIT  | 10 | Maximum ticks before a controlled shutdown/restart is performed  |
| SENSOR_ADDR  | 0x76 | BME280 sensor address  |
| SEND_BLOCK_SIZE  |  25 | Number of readings to be sent in one block after comm's restored  |
| SAMPLE_INTERVAL  | 55 | Time (in seconds) between sensor readings  |
| MIN_RETRY_TIME  | 15 | Default backoff time (in seconds) for comm's attempts  |
| MAX_RETRY_TIME  | 600 | Maximum backoff time (in seconds) for comm's attempts |

### AWS Specific
 
| Config Item | Default Value | Description |
|:-----|:-----|:-----|
| AWS_CLIENT_ID | 'IoT-1'   | A unique ID for the IoT device |
| AWS_ENDPOINT |  'data.iot.us-west-2.amazonaws.com'   | Target data center |
| AWS_ENDPOINT_PORT |  8883   | MQTT port to write to. Make sure the firewall knows about this  |
| AWS_ROOT_CA |  'certs/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem'   | Root certificate authority cert |
| AWS_PRIVATE_KEY_PATH |  'certs/12345-private.pem.key'   | Path to the private client key|
| AWS_CERT_PATH |  'certs/12345-certificate.pem.crt'   | Path to the certificate |
| AWS_CLIENT_TOPIC |  'sdk/test/java'   | Client MQTT topic to publish to.   | 

**Note:** For AWS certificate generation, see [Create and Activate a Device Certificate ](https://docs.aws.amazon.com/iot/latest/developerguide/create-device-certificate.html)




