# lambda_aws_cloudtrail_automation
Below is what this code does:
1. Create S3 Bucket for cloudtrail.
2. Create KMS Key
3. Create Trail

Script is idempotent so resources with similar names will not be created

## Usage

Below are the variables to be updated in ideal_policy.json file:
``` JSON
    "s3_bucket_name" : "bucket prefix user want to give to his bucket",
    "region_name" : "Region where bucket should be created",
    "account_number" : "User's aws account number",
 ```
 Apart from above mentioned variables, User need to replace below values in **ideal_policy.json** accordingly:
 1. Your_Account_ID
 2. Admin_User_Id
 
 ## Resources Created:
 
     S3 bucket is created by name: bucket_prefix-account_number-region_name
     kms key by name: bucket_prefix-account_number-region_name
     Cloud trail name : bucket_prefix-account_number-region_name
 
     
        
   
