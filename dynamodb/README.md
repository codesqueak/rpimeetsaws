# Amazon DynamoDB

[Official Documentation](https://aws.amazon.com/dynamodb/)

<img src="../images/dynamodb.png">

The application stores recorded information in DynamoDB.  Entries are partitioned by date and ordered by minute in day. 
The data is written by a simple Lambda which receives raw JSON from an IoT device topic.

The data is formatted as below:

```json
{
  "caldate": "27-08-2018",
  "calminute": 4,
  "msg-id": "c7f07595-a4a2-4442-af90-2003282efe16",
  "pihum0": "89.57",
  "pipress0": "997.54",
  "pitemp0": "16.27"
}
```

The fields in the JSON are defined as:

| Field | Definition |
|:--------|:-----------| 
| caldate	| Date of data capture, format DD-MM-YYYY  |
| calminute	| Minute of capture day, range 0..1440  |
| msg-id	| Unique message identifier, UUID  |
| pihum0	| Humidity value, % range 0.0..100.00 |
| pipress0	| Pressure value, range 300..1100 hPa)   |
| pitemp0	| Temperatue value, range -40…85°C |

The table to hold the IoT data is defined as a simple key/value mapping with the following structure:

| Details | Value |
|:--------|:-----------| 
| Table Name	| aws-iot-java |
| Primary partition key	| caldate (String) |
| Primary sort key	| calminute (Number) |

This allows the data to be selected on a day to day basis, ordered by capture time.

## Creation Script

Command: `aws dynamodb create-table --table-name <schema file name>.json`

Schema file:

```json
{
   "AttributeDefinitions":[
      {
         "AttributeName":"caldate",
         "AttributeType":"S"
      },
      {
         "AttributeName":"calminute",
         "AttributeType":"N"
      }
   ],
   "KeySchema":[
      {
         "KeyType":"HASH",
         "AttributeName":"caldate"
      },
      {
         "KeyType":"RANGE",
         "AttributeName":"calminute"
      }
   ],
   "ProvisionedThroughput":{
      "WriteCapacityUnits":5,
      "ReadCapacityUnits":5
   },
   "TableName":"aws-iot-java"
}
```








