# Amazon S3 / Route 53

[Official Documentation for S3](https://aws.amazon.com/s3/)

<img src="../images/s3.png">

[Official Documentation for Route 53](https://aws.amazon.com/route53/)

<img src="../images/route53.png">

## Usage

S3 is being used as a general storage for the application web site files.  A very useful feature in S3 is that the files stored can be declared to be a webs site and published as such.
This does away with a need to deploy a specific web server. This can be associated with a custom domain name registered in Route 53.

## Configure Web Site

Publishing a static web site via S3 is a simple process involving the following steps:

- [ ] Create a bucket in S3. Important - make this the same name as the site being published. E.g. bucket name - mystaticwebsite.net
- [ ] Upload files to the bucket
- [ ] In S3/Properties, select 'Static website hosting'. You can select the index and error pages here. This will give you an endpoint such as http://mystaticwebsite.net.s3-website-us-west-2.amazonaws.com
- [ ] Add a policy to S3 -> Permissions -> Bucket Policy,to allow the site to be read (See below for sample policy). *Warning* - The site is now visible to the world!
- [ ] Use the endpoint in a browser to confirm that the site is 'live'

### Sample Policy

```json
{
  "Version":"2012-10-17",
  "Statement":[{
	"Sid":"PublicReadGetObject",
        "Effect":"Allow",
	  "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::mystaticwebsite.net/*"
      ]
    }
  ]
}
```
*Note:* The name of your bucket needs to go into the `Resource` field

## Configuring DNS

Once the site is verified as being 'live', it is possible to access it via a custom domain name using the following steps:

- [ ] Go to the Route 53 [page](https://console.aws.amazon.com/route53/home)
- [ ] Follow the wizard to register a domain. This name *MUST* match the bucket name
- [ ] Select the `Hosted Zone` tab and select the domain name you just registered
- [ ] Create two record sets, one for `mystaticwebsite.net` and one for `mystaticwebsite.net`. Refer to the AWS documentation for [details](https://docs.aws.amazon.com/AmazonS3/latest/dev/website-hosting-custom-domain-walkthrough.html).
- [ ] Check you now have access to the website via the domain
  
