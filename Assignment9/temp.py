import boto3
from operator import itemgetter


def list_oldest_files(bucket_name):
    s3_client = boto3.client("s3")

    # List objects in the bucket
    paginator = s3_client.get_paginator("list_objects_v2")
    objects = []

    for page in paginator.paginate(Bucket=bucket_name):
        if "Contents" in page:
            objects.extend(page["Contents"])

    # Sort objects by LastModified date
    sorted_objects = sorted(objects, key=itemgetter("LastModified"))

    # Print the files sorted by oldest first
    for obj in sorted_objects:
        print(f"File: {obj['Key']}, Last Modified: {obj['LastModified']}")


# Replace 'your-bucket-name' with your S3 bucket name
list_oldest_files("your-bucket-name")
