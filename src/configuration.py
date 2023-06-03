import boto3
import logging

ec2_client = boto3.client('ec2')
response = ec2_client.describe_security_groups(
    Filters=[
        {
            'Name': 'group-name',
            'Values': ['webserver-sg-number-one']
        }
    ]
)

security_groups = response['SecurityGroups']
security_group_id = security_groups[0]['GroupId']
if security_group_id is None:
    logging.error("Dont have other manager ip!")
    raise NotImplementedError("Dont have other manager ip!")
    

if security_groups:
    security_group_id = security_groups[0]['GroupId']
instance_type = 't2.micro'
ami_id = 'ami-041c36ce1b70dfc41'
idle_timeout_minutes = 15
region_name='us-east-1'
add_worker_endpoint='add-worker'
start_new_work_endpoint='can-you-start-work'
complete_task_endpoint='complete-task'
remove_worker_endpoint= 'remove-work'