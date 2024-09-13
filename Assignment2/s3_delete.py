import boto3
import logging
from datetime import datetime, timedelta, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize the S3 client
s3_client = boto3.client("s3")

# Define the S3 bucket name
BUCKET_NAME = "pk1-bucket"


def lambda_handler(event, context):
    # Get the current time in UTC and calculate the cutoff date (10 days ago)
    utc_now = datetime.now(timezone.utc)
    cutoff_date = utc_now - timedelta(days=10)

    # List objects in the specified bucket
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

    if "Contents" not in response:
        logger.info("No objects found in the bucket.")
        return

    deleted_objects = []

    for obj in response["Contents"]:
        # Get the last modified date of the object
        last_modified = obj["LastModified"]

        # Compare the last modified date with the cutoff date
        if last_modified < cutoff_date:
            # Delete the object
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=obj["Key"])
            deleted_objects.append(obj["Key"])
            logger.info(f'Deleted object: {obj["Key"]}')

    # Log the deleted objects
    if deleted_objects:
        logger.info("Deleted objects:")
        for deleted_object in deleted_objects:
            logger.info(deleted_object)
    else:
        logger.info("No objects older than 30 days were found.")

    return {"statusCode": 200, "body": "Process completed"}
