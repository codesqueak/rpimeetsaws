# Amazon CloudFront

[Official Documentation for CloudFront](https://aws.amazon.com/cloudfront/)

<img src="../images/cloudfront.png">

CloudFront is a massively scaled and globally distributed content delivery network (CDN) with a number of features directly useful to this application.

## Features in Brief

* A large number of globally distributed points of presence (PoP)
* Regional edge caches
* SSL/TLS Encryptions and HTTPS
* Access control - including user authentication and location restrictions
* Control on S3 access 
* Control on API access

## Usage

The application uses a number of CloudFront features:

* PoP's enables for EMEA / North America to enhance performance when accessing assets in S3
* Enabling HTTPS:// only access
* Removing public access to S3

## Notes on S3 / Route 53

If you are publishing a static web site (as in this case) via CloudFront, ignore the policy and DNS configuration in the section on S3.  
CloudFront can make all the necessary DNS updates and policy changes required when publishing authomatically and without further intervention.


