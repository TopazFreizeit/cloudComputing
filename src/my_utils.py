import logging
import boto3
import requests
import redis

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

# Get Public IP
def get_redis_public_ip():
    instance_name = 'InfraStack/redis-instance'
    # Create a Boto3 EC2 client
    ec2_client = boto3.client('ec2', region_name='us-east-1')

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