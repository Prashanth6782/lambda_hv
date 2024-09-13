import boto3
import time

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    # Step 1: Define the EC2 instance ID
    instance_id = "i-089938dd7ebc7d8f3"  # Replace with your EC2 instance ID

    # Step 2: Fetch instance details to get volume type, instance type, and image ID
    print("Fetching instance details...")
    instance_details = ec2.describe_instances(InstanceIds=[instance_id])
    instance = instance_details["Reservations"][0]["Instances"][0]

    # Fetching the required details from the running instance
    availability_zone = instance["Placement"]["AvailabilityZone"]
    instance_type = instance["InstanceType"]
    image_id = instance["ImageId"]
    volume_id = instance["BlockDeviceMappings"][0]["Ebs"]["VolumeId"]
    volume_type = instance["BlockDeviceMappings"][0]["Ebs"].get("VolumeType", "gp2")

    print(
        f"Instance Type: {instance_type}, Image ID: {image_id}, Volume ID: {volume_id}, Volume Type: {volume_type}"
    )
    print(f"Availability Zone: {availability_zone}")

    # Step 3: Fetch the latest snapshot for the instance's root EBS volume
    print("Fetching the most recent snapshot...")

    # Find the latest snapshot for this volume
    snapshots = ec2.describe_snapshots(
        Filters=[{"Name": "volume-id", "Values": [volume_id]}],
        OwnerIds=["self"],  # Filter for snapshots owned by your account
    )

    snapshots_sorted = sorted(
        snapshots["Snapshots"], key=lambda x: x["StartTime"], reverse=True
    )
    latest_snapshot_id = snapshots_sorted[0]["SnapshotId"]
    print(f"Latest snapshot ID: {latest_snapshot_id}")

    # Step 4: Get the volume size, with a fallback in case 'VolumeSize' is missing
    volume_size = instance["BlockDeviceMappings"][0]["Ebs"].get(
        "VolumeSize", 8
    )  # Defaulting to 8 GiB if not found
    print(f"Using volume size: {volume_size} GiB")

    # Step 5: Launch a new EC2 instance with the restored volume (no need to create volume explicitly)
    print("Launching a new EC2 instance...")
    new_instance = ec2.run_instances(
        ImageId=image_id,  # Use the same Image ID as the original instance
        InstanceType=instance_type,  # Use the same instance type as the original
        MinCount=1,
        MaxCount=1,
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/xvda",  # The device name
                "Ebs": {
                    "SnapshotId": latest_snapshot_id,
                    "VolumeSize": volume_size,  # Use the same or fallback volume size
                    "DeleteOnTermination": True,
                    "VolumeType": volume_type,  # Use the same volume type
                },
            }
        ],
    )

    new_instance_id = new_instance["Instances"][0]["InstanceId"]
    print(f"New EC2 instance launched with ID: {new_instance_id}")

    return {
        "statusCode": 200,
        "body": f"New EC2 instance {new_instance_id} created successfully from snapshot {latest_snapshot_id}.",
    }
