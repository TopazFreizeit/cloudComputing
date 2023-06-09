import base64
import logging
import boto3
import requests
import redis
import time

# Logger
# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler to write logs to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Create a formatter for the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Get the root logger
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
# Create a Boto3 EC2 client
ec2_client = boto3.client('ec2', region_name='us-east-1')
ec2_resource = boto3.resource('ec2',region_name="us-east-1")

# Get Public IP
def get_redis_public_ip():
    instance_name = 'InfraStack/redis-instance'

    # Describe instances with the specified name tag
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [instance_name]
            }
        ]
    )

    # Extract the public IP address from the response
    if 'Reservations' in response:
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if 'PublicIpAddress' in instance:
                    return instance['PublicIpAddress']

    return None


def get_my_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    my_ip = response.json()['ip']
    return my_ip

redis_public_ip = get_redis_public_ip()
my_ip = get_my_public_ip()
logging.info(f'redis public ip {redis_public_ip}, my ip {my_ip}')

if redis_public_ip is None or my_ip is None:
    logging.error(f'redis public ip {redis_public_ip} or my ip {my_ip} is none')
    raise RuntimeError("Dont public ip of redis or myself!")

my_redis = redis.Redis(host=redis_public_ip, port=6379, db=0)

## wait for redis connection
ok = False
while not ok:
    try:
        my_redis.get("ddnkjn")
        ok = True
        logging.info("have connection with Redis")
    except Exception:
        logging.warn("do not have connection with Redis")
        time.sleep(10)

def kill_myself():
    logging.info("want to kill my self")
    # Get the token
    token_url = "http://169.254.169.254/latest/api/token"
    token_ttl = "21600"

    token_headers = {
        "X-aws-ec2-metadata-token-ttl-seconds": token_ttl
    }

    response = requests.put(token_url, headers=token_headers)
    token = response.text.strip()
    logging.info(f"token is {token}")

    if response.status_code == 200:
        # Fetch metadata using the token
        metadata_url = "http://169.254.169.254/latest/meta-data/instance-id"
        metadata_headers = {
            "X-aws-ec2-metadata-token": token
        }

        metadata_response = requests.get(metadata_url, headers=metadata_headers)
        instance_id = metadata_response.text
        logging.info(f"instance_id is {instance_id}")

        if metadata_response.status_code == 200:
            response = ec2_client.terminate_instances(InstanceIds=[instance_id])
            logging.info(f"just killed myself and got the response {response}")
        else:
            logging.error(f"Metadata request failed with status code {metadata_response.status_code}")
    else:
        logging.error(f"Token request failed with status code {response.status_code}")

def create_new_ec2_instance_worker():
    logging.info(f'want to create new instance worker')
    security_group = list(ec2_resource.security_groups.filter(Filters=[{'Name': 'group-name', 'Values': ['webserver-and-redis-SG']}]))[0] # type: ignore
    logging.info(f'security group to add is: {security_group}')
    user_data="#!/bin/bash\n"
    user_data = user_data + """yum update -y
    yum install -y git
    yum install -y python3
    yum install -y python3-pip
    pip3 install urllib3==1.26.6  boto3
    pip3 install redis
    pip3 install fastapi
    pip3 install requests
    pip3 install "uvicorn[standard]"
    git clone https://github.com/TopazFreizeit/cloudComputing.git
    cd cloudComputing
    cd src
    python3 worker.py
    """
    instance = ec2_resource.create_instances( # type: ignore
        ImageId='ami-0715c1897453cabd1',
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        UserData=user_data,
        SecurityGroups=[security_group.group_name],
    )
    # Wait for the instance to be running
    logging.info('wait for instance to start running')
    instance[0].wait_until_running()

    # Get the public IP address of the new instance
    public_ip = ec2_resource.Instance(instance[0].id).public_ip_address # type: ignore
    
    # Specify the instance ID
    instance_id = instance[0].id
    logging.info(f'Instance created successfully with ID: {instance_id}')
    logging.info(f'Public IP address: {public_ip}')
    
    # Wait for the instance to pass both status checks
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance_id])

    logging.info(f"Instance {instance_id} passed all health checks.")