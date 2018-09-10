# Amazon API Gateway

[Official Documentation](https://aws.amazon.com/api-gateway/)


## Method Request


## Integration Request


## Integration Response


## Method Response


## Authorizers




```json
{
    "TableName": "aws-iot-java",
    "KeyConditionExpression": "caldate=:v1",
    "ExpressionAttributeValues": {
        ":v1": {"S": "$input.params('caldate')"}
    },
    "ProjectionExpression": "calminute,pitemp0,pipress0,pihum0"
}
```


```json
{
    "TableName": "aws-iot-java",
    "KeyConditionExpression": "caldate=:v1",
    "ExpressionAttributeValues": {
        ":v1": {"S": "$input.params('caldate')"}
    },
    "ProjectionExpression": "calminute,pihum0"
}
```

