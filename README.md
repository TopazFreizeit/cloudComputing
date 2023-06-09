# Cloud Computing HW2

- Hey, welcome to our HW2 assigment for cloud computing course! :)

- You can run the **run.bat** file (for Windows) or **run.sh** file (for mac) in the parent directory _or_ follow the instructions below.

- if you ran the script you'll see the 2 public IP printed to the screen afte the deployment is finished.

## Instructions

1. Please install nodejs on your computer (node -v to confirm and check version)
2. Please install aws-cdk gloablly by typing "npm install -g aws-cdk"
3. Please go to "infra" folder and install all project dependencies using "npm install"
4. Please log in to your account
5. If it is the first time you use aws cdk please type "cdk bootstrap"
   - (Deploying stacks with the AWS CDK requires dedicated Amazon S3 buckets and other containers to be available to AWS CloudFormation during deployment)
6. For deployment please type "cdk deploy".
7. After deployment finished you will see the 2 endpoint node instance public IP printed to screen:
   - Outputs:
     InfraStack.InstancePublicIp = \<IP\>
8. Wait until the instance will stop to initialize (approx 5min) and browse to the public IP on port **8080**.

### Notes

1. All infrastructure will be deployed in us-east-1 region.
2. We used fastapi as the framework.
3. Please read the CDK documentation for typescript if needed - https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
