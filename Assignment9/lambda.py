import boto3
from datetime import datetime, timedelta
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3 = boto3.client("s3")

# Define the bucket name and age threshold
BUCKET_NAME = "your-bucket-name"
AGE_THRESHOLD = timedelta(days=180)  # 6 months


def lambda_handler(event, context):
    # Get the current date
    now = datetime.utcnow()
    logger.info(f"Current date: {now}")

    # List objects in the bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    # Check if bucket has objects
    if "Contents" not in response:
        logger.info("No objects found in the bucket.")
        return

    # Process each object
    for obj in response["Contents"]:
        key = obj["Key"]
        last_modified = obj["LastModified"]

        # Check if the object is older than the threshold
        if now - last_modified > AGE_THRESHOLD:
            logger.info(f"Archiving {key}, last modified on {last_modified}")

            # Change the storage class to Glacier
            s3.copy_object(
                Bucket=BUCKET_NAME,
                CopySource=f"{BUCKET_NAME}/{key}",
                Key=key,
                StorageClass="GLACIER",
            )

            logger.info(f"Archived {key} to Glacier.")
        else:
            logger.info(f"{key} is not older than 6 months, skipping.")

    return {"statusCode": 200, "body": "Archival process completed."}
