import boto3

# Create a session using your AWS credentials
session = boto3.Session(region_name='us-west-2')  # Replace with your preferred region

# Create an EC2 resource
ec2 = session.resource('ec2')

# Define the key pair name
key_pair_name = 'studentpk-key'

# Retrieve instances with the specified key pair
instances = ec2.instances.filter(
    Filters=[{'Name': 'key-name', 'Values': [key_pair_name]}]
)

# Collect instance IDs to terminate
instance_ids = [instance.id for instance in instances]

if instance_ids:
    # Terminate instances
    ec2.instances.filter(InstanceIds=instance_ids).terminate()
    print(f"Terminating instances: {', '.join(instance_ids)}")
else:
    print(f"No instances found with the key pair: {key_pair_name}")
