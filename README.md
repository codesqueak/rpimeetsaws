[![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

# Raspberry Pi Meets Iot Meets AWS

An IoT system using a Raspberry Pi Zero as an IoT device and AWS to host storage and web presence

<img width="240" height="144" src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Raspberry_Pi_B%2B_top.jpg/320px-Raspberry_Pi_B%2B_top.jpg">  <img width="288" height="216" src="images/iot.png">  <img width="240" height="144" src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Amazon_Web_Services_Logo.svg/320px-Amazon_Web_Services_Logo.svg.png"> 

## Logical Architecure

How the parts relate to each other
<p align="center">
  <img src="images/architecture.png">
</p>

## IoT Device 

Electronics Package and Supporting Software [Here](rpi/README.md)

## S3

Web site file storage and domain publishing [Here](s3/README.md)

## Cognito

User Sign-Up, Sign-In, and Access Control [Here](cognito/README.md)

## API Gateway

Create and publish a REST API [Here](gateway/README.md)

## DynamoDB

JSON data storage for IoT data [Here](dynamodb/README.md)

## Lambda

Processing of incoming data from IoT device(s) [Here](lambda/README.md)

## IoT Core

MQTT based interface for handling IoT devices [Here](iot/README.md)

# Example Data Output

<img src="images/graph.png">







