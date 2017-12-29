#!/usr/local/bin/python3.3
import boto3
import json
import time

def lambda_handler(event, context):
    TrailCreate = Boto3Trails()
    TrailCreate.create_trail()


class Boto3Trails:
    def __init__(self):
        self.policy_file = self.load_default_policy()
        self.bucket_prefix = self.policy_file["s3_bucket_name"]
        self.region_name = self.policy_file["region_name"]
        self.account_number = self.policy_file["account_number"]
        self.bucket_policy = json.dumps(self.policy_file["trail_policy"])
        self.kms_policy = json.dumps(self.policy_file['kms_policy'])
        self.s3_client = boto3.client('s3', 
                                      region_name=self.region_name)
        self.s3_resource = boto3.resource('s3', 
                                          region_name=self.region_name)
        self.ctrail_client = boto3.client('cloudtrail', 
                                      region_name=self.region_name)

        self.kms_policy = json.dumps(self.policy_file['kms_policy'])
        self.kms_client = boto3.client('kms', 
                                  region_name=self.region_name)

    @classmethod
    def load_default_policy(cls):
        with open('ideal_policy.json') as json_data:
            data = json.load(json_data)
        return data

    def get_buckets(self):
        get_buckets = self.s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in get_buckets['Buckets']]
        return buckets

    def create_s3_bucket(self):
        existing_buckets = self.get_buckets()
        new_bucket_name = self.bucket_prefix+"-"+self.account_number+"-"+self.region_name
        if new_bucket_name in existing_buckets:
            pass
        else:
            bucket_created= self.s3_client.create_bucket(Bucket=new_bucket_name, ACL='private', CreateBucketConfiguration ={'LocationConstraint': self.region_name})
            update_bucket_policy = self.s3_client.put_bucket_policy(Bucket=new_bucket_name, Policy = self.bucket_policy)

        return new_bucket_name

    def list_alias(self):
        key_info_list = list()
        alias_name = 'alias/' + self.bucket_prefix + "-" + self.account_number + "-" + self.region_name
        get_aliases = self.kms_client.get_paginator('list_aliases')
        alias_iterator = get_aliases.paginate()
        for alias in alias_iterator:
            for sub_alias in alias['Aliases']:
                if 'alias/aws' not in sub_alias['AliasName']:
                    key_info =(sub_alias['AliasName'], sub_alias['TargetKeyId'])
                    key_info_list.append(key_info)
        if [item for item in key_info_list if alias_name in item]:
            targetid = ([item for item in key_info_list if alias_name in item])[0]
            return targetid[1]
        else:
            return self.create_kms_key()

    def create_kms_key(self):
        alias_name = 'alias/' + self.bucket_prefix + "-" + self.account_number + "-" + self.region_name
        if alias_name not in self.list_alias():
            create_key = self.kms_client.create_key(Policy=self.kms_policy, Description="AWS", KeyUsage='ENCRYPT_DECRYPT', Tags=[
                {
                    'TagKey': 'name',
                    'TagValue': 'bototestkey'
                },
                {
                    'TagKey': 'Name',
                    'TagValue': 'bototestkey'
                },
            ])
            create_alias = self.kms_client.create_alias(
                AliasName=alias_name,
                TargetKeyId=create_key['KeyMetadata']['KeyId']
            )

            print("The id of newly created key is: ", create_key['KeyMetadata']['KeyId'])
            return (create_key['KeyMetadata']['KeyId'])
        else:
            print("The key is already created, Key name: ", alias_name)

    def create_trail(self):
        trail_name = self.create_s3_bucket()
        describe_trail= self.ctrail_client.describe_trails(trailNameList=[trail_name])
        if not describe_trail['trailList']:
            trail_create = self.ctrail_client.create_trail(Name=trail_name, S3BucketName=trail_name,
                                                           IncludeGlobalServiceEvents=True, IsMultiRegionTrail=True,
                                                           EnableLogFileValidation=True,
                                                           KmsKeyId=self.list_alias())
            trail_arn = "arn:aws:cloudtrail:" + self.region_name + ":" + self.account_number + ":trail/" + trail_name
            start_logging = self.ctrail_client.start_logging(Name=trail_arn)
            print("new trail is created and logging is enabled. The trail name & corresponding bucket name are same, that is: ",trail_name)
        else:
            print("The trail ",trail_name, " already exists")

# TrailCreate = Boto3Trails()
# TrailCreate.create_trail()
#print(TrailCreate.list_alias())
