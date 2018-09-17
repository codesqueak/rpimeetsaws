# Amazon Cognito

[Official Documentation](https://aws.amazon.com/cognito/)

<img src="../images/cognito.png">

The simplest way to add user sign-up, sign-in, and access control to your web applications, REST interfaces and mobile apps in the AWS world is 
by using Amazon Cognito.

This application uses Cognito to:

* Control access to the REST endpoint from the [web application](../s3/README.md)
* Handle user creation requests
* Handle user login requests

For this application, Cognito was configured with one *User Pool*, with account creation requests being handled manually via the AWS console.

**Note:** Access of IoT applications to MQTT is handled via x509n certification, rather than via Cognito.






