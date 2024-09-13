import boto3

# Create a session using your AWS credentials
session = boto3.Session(region_name="us-west-2")  # Replace with your preferred region

# Create an EC2 resource
ec2 = session.resource("ec2")

# Define instance parameters
instances = ec2.create_instances(
    ImageId="ami-0e42b3cc568cd07e3",  # Replace with your desired AMI ID
    InstanceType="t4g.nano",          # Replace with your desired instance type
    MinCount=2,                       # Create 2 instances
    MaxCount=2,                       # Create up to 2 instances
    KeyName="studentpk-key",          # Replace with your key pair name
    # UserData=Stopup_script         # Optional: pass Stopup script if needed
    # SecurityGroupIds=['sg-0123456789abcdef0'],  # Optional: replace with your security group ID
    # SubnetId='subnet-0123456789abcdef0'        # Optional: replace with your subnet ID
)

# Iterate over the created instances
for i, instance in enumerate(instances, start=1):
    # Wait for the instance to be running
    instance.wait_until_running()

    # Reload instance attributes
    instance.reload()

    # Add tags to the instance
    instance.create_tags(
        Tags=[
            {"Key": "Name", "Value": f"Auto-Stop-{i}"},  # Name tag
            {"Key": "pk1", "Value": "Auto-Stop"},         # pk1 tag
        ]
    )

    # Print instance details
    print(f"Instance created: {instance.id}")
    print(f"Instance name set to: Auto-Stop-{i}")
