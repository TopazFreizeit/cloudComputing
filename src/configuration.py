import os


instance_type = 't2.micro'
ami_id = 'ami-041c36ce1b70dfc41'
idle_timeout_minutes = 15
region_name='us-east-1'


security_group_id = os.getenv('SECURITY_GROUP_ID')
if security_group_id is None:
    raise NotImplementedError("Dont have security_group_id")

subnet_id = os.getenv('SUBNET_ID')
if subnet_id is None:
    raise NotImplementedError("Dont have subnet_id")

add_worker_endpoint='add-worker'
start_new_work_endpoint='can-you-start-work'
complete_task_endpoint='complete task'