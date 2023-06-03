import boto3
import logging

instance_type = 't2.micro'
ami_id = 'ami-041c36ce1b70dfc41'
idle_timeout_minutes = 15
region_name='us-east-1'
add_worker_endpoint='add-worker'
start_new_work_endpoint='can-you-start-work'
complete_task_endpoint='complete-task'
remove_worker_endpoint= 'remove-work'