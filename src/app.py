# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import csv
import json
import os
import urllib

import boto3

s3_client = boto3.client('s3')
datasync_client = boto3.client('datasync')

# Configuration
log_group_arn=os.environ.get('LOG_GROUP_ARN')

def schedule_task(task_name, include_filter_pattern, exclude_filter_pattern, source_location_arn, destination_location_arn):
    try:
        # Create Task
        excludes = []
        if (exclude_filter_pattern):
            excludes.append({
                'FilterType': 'SIMPLE_PATTERN',
                'Value': exclude_filter_pattern
            })

        includes = []
        if (include_filter_pattern):
            includes.append({
                'FilterType': 'SIMPLE_PATTERN',
                'Value': include_filter_pattern
            })

        create_task_response = datasync_client.create_task(
            SourceLocationArn=source_location_arn,
            DestinationLocationArn=destination_location_arn,
            CloudWatchLogGroupArn=log_group_arn,
            Name=task_name,
            Options={
                'VerifyMode': 'ONLY_FILES_TRANSFERRED',
                'Atime': 'BEST_EFFORT',
                'Mtime': 'PRESERVE',
                'Uid': 'INT_VALUE',
                'Gid': 'INT_VALUE',
                'PreserveDeletedFiles': 'PRESERVE',
                'PreserveDevices': 'NONE',
                'PosixPermissions': 'PRESERVE',
                'BytesPerSecond': -1,
                'TaskQueueing': 'ENABLED',
                'LogLevel': 'TRANSFER'
            },
            Excludes=excludes
        )

        # Schedule task execution w/optional Includes filter
        start_task_response = datasync_client.start_task_execution(
            TaskArn=create_task_response['TaskArn'],
            Includes=includes,
        )
        return start_task_response
    except Exception as e:
        print("Error creating/executing DataSync tasks. TaskName: {}, IncludeFilterPattern: {}, ExcludeFilterPattern: {}, Exception: {}".format(task_name, include_filter_pattern, exclude_filter_pattern, e))
        raise e

def handler(event, context):
    # Log the event.
    print("Received event: " + json.dumps(event, indent=2))

    try:
        # Get the object from the event.
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

        #Read S3 File to act on each filter
        csv_file = s3_client.get_object(Bucket=bucket, Key=key)
        rows = csv_file['Body'].read().decode('utf-8').split()
        data = csv.DictReader(rows)
        for record in data:
            # Note! If you file encoding is utf-8-bom then you need the little "uefeff" preamble.
            # task_name = record['\ufeffTaskName']
            task_name = record['TaskName']
            include_filter_pattern = record['IncludeFilterPattern']
            exclude_filter_pattern = record['ExcludeFilterPattern']
            source_location_arn = record['SourceLocationArn']
            destination_location_arn = record['DestinationLocationArn']
            print("Processing TaskName {}".format(task_name))
            schedule_task(task_name, include_filter_pattern, exclude_filter_pattern, source_location_arn, destination_location_arn)

        return 'Success'
    except Exception as e:
        print("Error processing object {} from bucket {}. Event {}".format(key, bucket, json.dumps(event, indent=2)))
        raise e
