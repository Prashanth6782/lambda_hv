import boto3
# check the timeout interval alone
# Initialize the S3 and EC2 clients
s3_client = boto3.client('s3')
ec2_client = boto3.client('ec2')

# Create a session using your AWS credentials
session = boto3.Session(
    region_name='us-west-2'  # Replace with your preferred region
)

def lambda_handler(event, context):
    # Get the S3 bucket name and object key (file name) from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Convert object_key to lowercase to handle case insensitivity
    object_key = object_key.lower()

    # Log the bucket and file name
    print(f"Bucket: {bucket_name}")
    print(f"File Uploaded: {object_key}")

    # Embedded startup script as a string (from your uploaded file)
    startup_script = """#!/bin/bash
LOGFILE="/var/log/startup_script.log"

log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOGFILE
}

exec > >(tee -a $LOGFILE) 2>&1

log "Starting startup script."
log "Updating package lists..."
apt-get update

if ! command -v sudo &> /dev/null
then
    log "sudo not found, installing..."
    apt-get install -y sudo
else
    log "sudo is already installed."
fi

log "Installing nginx..."
apt-get install -y nginx

CUSTOM_HTML="/var/www/html/index.html"
log "Creating custom index.html..."
mkdir -p /var/www/html
bash -c "cat > $CUSTOM_HTML" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>My Custom Page</title>
</head>
<body>
    <h1>Welcome to My Custom Page!</h1>
    <p>This is a simple HTML page served by Nginx on an EC2 instance.</p>
</body>
</html>
EOF

log "Setting permissions..."
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

log "Restarting nginx..."
systemctl restart nginx

log "Enabling nginx to start on boot..."
systemctl enable nginx

log "Setup complete!"
"""

    # Check if the uploaded file is 'start.png'
    if object_key == 'start.png':
        # First, check if an instance with the tag already exists
        existing_instances = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['pk1-ec2-instance-lmbda']
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['pending', 'running']
                }
            ]
        )

        if existing_instances['Reservations']:
            print("An EC2 instance with the name 'pk1-ec2-instance-lmbda' is already running.")
            return {
                'statusCode': 200,
                'body': 'An EC2 instance is already running.'
            }

        # Create an EC2 resource if no instance exists
        ec2 = session.resource('ec2')

        # Define instance parameters and create the instance
        instances = ec2.create_instances(
            ImageId='ami-0e42b3cc568cd07e3',  # Replace with your desired AMI ID
            InstanceType='t4g.nano',          # Replace with your desired instance type
            MinCount=1,                       # Ensure only 1 instance is created
            MaxCount=1,                       # Ensure only 1 instance is created
            KeyName='studentpk-key',          # Replace with your key pair name
            UserData=startup_script,          # Pass the startup script as UserData
            # SecurityGroupIds=['sg-0123456789abcdef0'],  # Uncomment and replace with your security group ID
            # SubnetId='subnet-0123456789abcdef0'         # Uncomment and replace with your subnet ID
        )

        instance = instances[0]

        # Wait for the instance to be running
        instance.wait_until_running()

        # Reload instance attributes
        instance.reload()

        # Add a Name tag to the instance **after it's running**
        instance.create_tags(Tags=[{'Key': 'Name', 'Value': 'pk1-ec2-instance-lmbda'}])

        # Log instance details
        print(f"Instance created: {instance.id}")
        print(f"Instance name set to: pk1-ec2-instance-lmbda")
        
        return {
            'statusCode': 200,
            'body': f'Successfully started EC2 instance: {instance.id} with Name tag: pk1-ec2-instance-lmbda'
        }

    # Check if the uploaded file is 'stop.png'
    elif object_key == 'stop.png':
        # Terminate the EC2 instance
        response = ec2_client.terminate_instances(InstanceIds=['i-0abcdef1234567890'])
        print(f"Terminating EC2 instance: i-0abcdef1234567890")
        return response

    else:
        print(f"File uploaded is not a recognized command: {object_key}")
        return {
            'statusCode': 400,
            'body': 'Invalid file uploaded. Upload start.png to start an instance or stop.png to terminate an instance.'
        }
