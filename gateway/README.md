# Amazon API Gateway

[Official Documentation](https://aws.amazon.com/api-gateway/)

<img src="../images/gateway.png">

A simple API was defined in the API Gateway console.  A set of resource endpoints where defined as follows:

* GET  /all/{caldate}
* GET /humonly/{caldate}
* GET /pressonly/{caldate}
* GET /temponly/{caldate}

These are designated to return all data, humidity, pressure or temperature, on one specific day `{caldate}`

**Note:** When creating a resource endpoint, the console will prompt to see if CORS should be enabled.  Selecting this 
will generate a matching `OPTIONS` endpoint with all necessary configuration. *YOU WILL NEED THIS!*

## Method Request

The method executions are left as default as no special configuration is required

## Integration Request

The integration requests ate configured to access DynamoDB directly.  To do this, select:

- [ ] Integration type - AWS Service
- [ ] AWS S=service - DynamoDB
- [ ] HTTP Method - POST
- [ ] Action - Query
- [ ] Execution role - You will need to define a role in IAM with the following policies `AmazonAPIGatewayPushToCloudWatchLogs` & `AmazonDynamoDBReadOnlyAccess`

### Mapping Templates

A template needs to be defined.  This is the query used to map data from DynamoDB to the response body.  For example, to read humidy data, add a mapping for the `application/json` 
content type.

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

## Integration Response

The integration response is left as default as no special configuration is required

## Method Response

The method response is left as default as no special configuration is required

## Authorizers

An authorizer is required for API Gateway calls.  This should be configured to point to the User Pool you have defined in Cognito. Only users authorized there 
will be able to access the API.
