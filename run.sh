#!/bin/zsh
echo "Enter AWS account id"  
read AWS_ACOUNT_ID
echo "Enter AWS acces key"  
read AWS_ACCESS_KEY_ID
echo "Enter AWS secret access key"  
read AWS_SECRET_ACCESS_KEY
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
export AWS_ACOUNT_ID=${AWS_ACOUNT_ID}
aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
cd infra
cdk deploy