echo "Welcome to the AWS configuration script!"
echo "Please provide the following details:"

read -p "AWS Access Key ID: " access_key
read -p "AWS Secret Access Key: " secret_key
region_name="us-east-1"
read -p "Default output format [json]: " output_format

# Set default output format to JSON if user doesn't provide anything
if [ -z "$output_format" ]; then
  output_format="json"
fi

aws configure set aws_access_key_id $access_key
aws configure set aws_secret_access_key $secret_key
aws configure set region $region_name
aws configure set output $output_format

echo "AWS configuration complete!"

cd infra
npm install -g aws-cdk
npm install
cdk bootstrap
cdk deploy 

echo "After deploy complete you will get the public ip, but notice it will take some time for the ec2 to initilaize, so please wait 5 min."