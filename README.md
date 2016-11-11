### BucketList 

Web App To Create Wishlist Using Python Flask and MySQL 

# Installation

Follow the steps to setup the appication

* From mysql console, run procedures from procedure.sql
* In app.py, update mysql app.config with correct credentials
* In app.py, add app.secret_key, aws access key, aws secret key, bucket_name
* Signup, Add wish, Update wish, Delete Wish


To run Bucketist web apllication, run the following command in the Console

```sh
$ python app.py
```

# Amazon S3 

* Login to AWS portal (https://console.aws.amazon.com/console/home)
* AWS Services -> S3
* Create a bucket
* Make bucket public by adding bucket policy
```sh
{ "Version": "2008-10-17", "Statement": [{ "Sid": "AllowPublicRead", "Effect": "Allow", "Principal": { "AWS": "*" }, "Action": ["s3:GetObject"], "Resource": ["arn:aws:s3:::bucket/*" ] }] }
```
* Create AWS access keys
