@REM @echo off
@REM echo "Welcome to the AWS configuration script!"
@REM echo "Please provide the following details:"
@REM 
@REM set /p AWS_ACOUNT_ID="Enter AWS account id:"
@REM set /p AWS_ACCESS_KEY_ID="Enter AWS acces key:"
@REM set /p AWS_SECRET_ACCESS_KEY="Enter AWS secret access key:"
@REM set /p region_name="Default region name:"
@REM set /p output_format="Default output format [json]:":
@REM 
@REM aws configure set aws_access_key_id "%AWS_ACCESS_KEY_ID%"
@REM aws configure set aws_secret_access_key "%AWS_SECRET_ACCESS_KEY%"
@REM aws configure set region "%region_name%"
@REM aws configure set output "%output_format%"

echo "AWS configuration complete!"

cd infra
call npm install -g aws-cdk
call npm install
call cdk bootstrap
call cdk deploy 
echo "After deploy complete you will get the public ip, but notice it will take some time for the ec2 to initilaize, so please wait 5 min."

@REM @echo off
@REM echo Welcome to the AWS configuration script!
@REM echo Please provide the following details:

@REM set /p access_key=AWS Access Key ID:
@REM set /p secret_key=AWS Secret Access Key:
@REM set /p region_name=Default region name:
@REM set /p output_format=Default output format [json]:

@REM REM Set default output format to JSON if user doesn't provide anything
@REM if "%output_format%"=="" set output_format=json

@REM aws configure set aws_access_key_id %access_key%
@REM aws configure set aws_secret_access_key %secret_key%
@REM aws configure set region %region_name%
@REM aws configure set output %output_format%

@REM echo AWS configuration complete!