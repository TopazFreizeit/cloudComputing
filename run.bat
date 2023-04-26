@REM @echo off
echo "Welcome to the AWS configuration script!"
echo "Please provide the following details:"

set /p AWS_ACOUNT_ID="Enter AWS account id:"
set /p AWS_ACCESS_KEY_ID="Enter AWS acces key:"
set /p AWS_SECRET_ACCESS_KEY="Enter AWS secret access key:"
set /p region_name="Default region name:"
set /p output_format="Default output format [json]:":

echo "AWS configuration complete!"

cd infra
call npm install -g aws-cdk
call npm install
call cdk bootstrap
call cdk deploy 
echo "After deploy complete you will get the public ip, but notice it will take some time for the ec2 to initilaize, so please wait 5 min."
