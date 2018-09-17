# Amazon Lambda

[Official Documentation](https://aws.amazon.com/documentation/lambda/)

<img src="../images/lambda.png">

A simple Lambda is used to transfer data between the IoT system and DynamoDB.  This is executed when data appears on MQTT.

See the IoT documentation on how to add an Action to an IoT MQTT endpoint to trigger a Lambda. 

## Lambda Script

```javascript
// console.log('Loading function');
var AWS = require('aws-sdk');
var dynamodb = new AWS.DynamoDB();
var docClient = new AWS.DynamoDB.DocumentClient();

exports.handler = (event, context, callback) => {
    
//    console.log("event.msgid="+event.msgid);
//    console.log("event.temp="+event.temp);
//    console.log("event.pressure="+event.pressure);
    var tableName = "aws-iot-java";    
    
    var params = {
        TableName: 'aws-iot-java',
        Item: {
            'msg-id': event.msgid,
            'caldate': event.caldate,
            'calminute': event.calminute,
            'pitemp0': event.pitemp0,
            'pihum0': event.pihum0,
            'pipress0': event.pipress0
            
        }
    }
    
    docClient.put(params,  function(err, data) {
        if (err) {
            console.log('Error putting item into dynamodb failed: '+err);
        }
        else {
            console.log('great success: '+JSON.stringify(data, null, '  '));
        }
    });
};
```

## Function

The script is called with the data presented to MQTT.  The `event` holds the data send, `context` is so the 
function can interact with AWS Lambda to get useful runtime information such as time remaining, 
and `callback` can be used to explicitly return information back to the caller.

Writing to DynamoDB is achieved through a call to `put` using the `DocumentClient`.  Success / failure handling is achieved by a 
callback function supplied in the `put` call along side the data.




