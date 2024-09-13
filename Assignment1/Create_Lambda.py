import boto3
import json
import logging

# Initialize the boto3 EC2 client
ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    # Describe instances with specific tags
    filters_stop = [{'Name': 'tag:pk1', 'Values': ['Auto-Stop']}]
    filters_start = [{'Name': 'tag:pk1', 'Values': ['Auto-Start']}]

    # Get instances to stop
    stop_response = ec2_client.describe_instances(Filters=filters_stop)
    stop_instances = [
        i['InstanceId'] for r in stop_response['Reservations'] for i in r['Instances']
    ]

    # Get instances to start
    start_response = ec2_client.describe_instances(Filters=filters_start)
    start_instances = [
        i['InstanceId'] for r in start_response['Reservations'] for i in r['Instances']
    ]

    # Check and Stop instances
    instances_to_stop = []
    for instance_id in stop_instances:
        instance_description = ec2_client.describe_instances(InstanceIds=[instance_id])
        state = instance_description['Reservations'][0]['Instances'][0]['State']['Name']
        if state in ['running', 'pending']:  # Only stop if it's running or pending
            instances_to_stop.append(instance_id)
    
    if instances_to_stop:
        logger.info(f"Stopping instances: {instances_to_stop}")
        ec2_client.stop_instances(InstanceIds=instances_to_stop)

    # Check and Start instances
    instances_to_start = []
    for instance_id in start_instances:
        instance_description = ec2_client.describe_instances(InstanceIds=[instance_id])
        state = instance_description['Reservations'][0]['Instances'][0]['State']['Name']
        if state == 'stopped':  # Only start if it's stopped
            instances_to_start.append(instance_id)

    if instances_to_start:
        logger.info(f"Starting instances: {instances_to_start}")
        ec2_client.start_instances(InstanceIds=instances_to_start)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'StoppedInstances': instances_to_stop,
            'StartedInstances': instances_to_start
        })
    }
