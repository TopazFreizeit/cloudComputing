set /p AWS_ACOUNT_ID="Enter AWS account id":
set /p AWS_ACCESS_KEY_ID="Enter AWS acces key"
set /p AWS_SECRET_ACCESS_KEY="Enter AWS secret access key"

aws configure set aws_access_key_id "%AWS_ACCESS_KEY_ID%"
aws configure set aws_secret_access_key "%AWS_SECRET_ACCESS_KEY%"