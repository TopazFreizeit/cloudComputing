import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from "aws-cdk-lib/aws-s3";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import * as path from "path";

import {
  Role,
  PolicyStatement,
  ServicePrincipal,
  Effect,
} from "aws-cdk-lib/aws-iam";
import * as iam from "aws-cdk-lib/aws-iam";

export class InfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 👇 import default VPC
    const vpc = ec2.Vpc.fromLookup(this, "my-default-vpc", {
      isDefault: true,
    });

    // 👇 create a security group for the EC2 instance
    const webserverSG = new ec2.SecurityGroup(this, "webserver-sg", {
      vpc,
    });

    webserverSG.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(80),
      "allow HTTP traffic from anywhere"
    );

    // create the S3
    const bucket = new s3.Bucket(this, "MyBucket", {
      removalPolicy: cdk.RemovalPolicy.DESTROY, // This will force CloudFormation to delete the bucket even if it's not empty
    });

    var srcPath = path.join(`${__dirname}`, "..", "..", "src");
    new s3deploy.BucketDeployment(this, "MyBucketDeployment", {
      sources: [s3deploy.Source.asset(srcPath)],
      destinationBucket: bucket,
      destinationKeyPrefix: "src/",
    });

    // IAM role that allows access to S3
    const role = new Role(this, "FlaskInstanceRole", {
      assumedBy: new ServicePrincipal("ec2.amazonaws.com"),
    });

    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess")
    );

    // Add a policy to the S3 bucket to allow access from the instance role
    bucket.addToResourcePolicy(
      new iam.PolicyStatement({
        actions: ["*"],
        resources: [bucket.bucketArn + "/*"],
        principals: [role],
      })
    );

    // 👇 create the EC2 instance
    const ec2Instance = new ec2.Instance(this, "ec2-instance", {
      vpc: vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      securityGroup: webserverSG,
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T2,
        ec2.InstanceSize.MICRO
      ),
      machineImage: new ec2.AmazonLinuxImage({
        generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
      }),
      userData: ec2.UserData.forLinux({ shebang: "#!/bin/bash" }),
      role: role,
    });

    // 👇  user data script
    // Install Python and dependencies
    ec2Instance.addUserData("yum update -y");
    ec2Instance.addUserData("yum install -y python3");
    ec2Instance.addUserData("yum install -y python3-pip");
    ec2Instance.addUserData('pip3 install "uvicorn[standard]" fastapi');

    // Add Flask app
    ec2Instance.addUserData(
      `aws s3 cp s3://${bucket.bucketName} /home/ec2-user --recursive`
    );

    // Run Flask app
    ec2Instance.addUserData("cd /home/ec2-user/src");
    ec2Instance.addUserData("export FLASK_APP=/home/ec2-user/src/lpr.py");
    ec2Instance.addUserData("uvicorn main:app --host 0.0.0.0 --port 80");

    new cdk.CfnOutput(this, "InstancePublicIp", {
      value: ec2Instance.instancePublicIp,
    });
  }
}
