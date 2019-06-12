# Klue Static Resources

Common js/css/fonts used across Bazardelux web pages.

## AWS Setup

Here are instructions on how to setup DNS and cloudfront to serve files from
the static.bazardelux.com S3 bucket over both HTTP and HTTPS in a secure way,
so as to not trigger browsers security warnings.

### S3 bucket

All files in this project are uploaded to an S3 bucket
(static.bazardelux.com.s3-website-eu-central-1.amazonaws.com). This bucket has
the policy:

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "Allow Public Access to All Objects",
			"Effect": "Allow",
			"Principal": "*",
			"Action": "s3:GetObject",
			"Resource": "arn:aws:s3:::static.bazardelux.com/*"
		}
	]
}
```

And the CORS configuration:

```
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CORSRule>
        <AllowedOrigin>*.bazardelux.com</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>HEAD</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>Content-*</AllowedHeader>
        <AllowedHeader>Host</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

This CORS setup is required to allow javascript loaded from
https://bazardelux.com to pre-fetch and load content from
https://static.bazardelux.com without triggering security warnings.

### Cloudfront setup

In order to serve static files through both HTTP and HTTPS, a cloudfront CDN is
configured on top of the S3 bucket static.bazardelux.com.

This cloudfront distribution has the following custom settings:

```
Distribution ID	EF9H1Y4D1AD2V
ARN	arn:aws:cloudfront::709131356479:distribution/EF9H1Y4D1AD2V
Log Prefix	-
Delivery Method	Web
Cookie Logging	Off
Distribution Status	Deployed
Comment	-
Price Class	Use Only US, Canada and Europe            <= CUSTOM
AWS WAF Web ACL	-
State	Enabled
Alternate Domain Names (CNAMEs) static.bazardelux.com        <= CUSTOM
SSL Certificate	static.bazardelux.com (d2b7c02a-0405-4475-b98b-50848c6204b2)         <= CUSTOM
Domain Name	d2crpjvtly4f5d.cloudfront.net
Custom SSL Client Support	Only Clients that Support Server Name Indication (SNI)
Default Root Object	index.html
Last Modified	2016-08-30 17:20 UTC+2
Log Bucket
```

It uses a custom certificate created via the aws console for the domain
'static.bazardelux.com'.

### Route 53 setup

Finally, we need an A record of type alias pointing static.bazardelux.com to
the cdn (d2crpjvtly4f5d.cloudfront.net in that case).

### Building new bundles

TODO

### Deploying

Run:

```
./publish.sh
```