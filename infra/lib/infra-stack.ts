import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from "aws-cdk-lib/aws-s3";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as path from "path";

import { Role, ServicePrincipal } from "aws-cdk-lib/aws-iam";
import * as iam from "aws-cdk-lib/aws-iam";

export class InfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 👇 import default VPC
    const vpc = ec2.Vpc.fromLookup(this, "my-default-vpc", {
      isDefault: true,
    });

    // 👇 create a security group for the EC2 instance
    const webserverSG = new ec2.SecurityGroup(this, "webserver-sg-number-one", {
      vpc: vpc,
      securityGroupName: "webserver-sg-number-one",
    });

    webserverSG.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(80),
      "allow HTTP traffic from anywhere"
    );

    // IAM role that allows access to S3
    const role = new Role(this, "InstanceRole", {
      assumedBy: new ServicePrincipal("ec2.amazonaws.com"),
    });

    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonEC2FullAccess")
    );

    const ec2Instance_1 = new ec2.Instance(this, "ec2-instance-1", {
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

    const ec2Instance_2 = new ec2.Instance(this, "ec2-instance-2", {
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

    // user data script of 1
    ec2Instance_1.addUserData("yum update -y");
    ec2Instance_1.addUserData("yum install -y git");
    ec2Instance_1.addUserData("yum install -y python3");
    ec2Instance_1.addUserData("yum install -y python3-pip");
    ec2Instance_1.addUserData('pip3 install "uvicorn[standard]" fastapi');
    ec2Instance_1.addUserData(
      "git clone https://github.com/TopazFreizeit/cloudComputing.git"
    );
    ec2Instance_1.addUserData("cd src");
    ec2Instance_1.addUserData("cd cd cloudComputing");
    ec2Instance_1.addUserData(
      "uvicorn main_manager:app --host 0.0.0.0 --port 80"
    );

    new cdk.CfnOutput(this, "InstanceOnePublicIp", {
      value: ec2Instance_1.instancePublicIp,
    });

    // 👇  user data script
    // Install Python and dependencies
    ec2Instance_2.addUserData("yum update -y");
    ec2Instance_2.addUserData("yum install -y git");
    ec2Instance_2.addUserData("yum install -y python3");
    ec2Instance_2.addUserData("yum install -y python3-pip");
    ec2Instance_2.addUserData('pip3 install "uvicorn[standard]" fastapi');
    ec2Instance_2.addUserData(
      "git clone https://github.com/TopazFreizeit/cloudComputing.git"
    );
    ec2Instance_2.addUserData("cd src");
    ec2Instance_2.addUserData("cd cd cloudComputing");
    ec2Instance_2.addUserData(
      `export OTHER_MANAGER_IP=${ec2Instance_1.instancePublicIp}`
    );
    ec2Instance_2.addUserData(
      "uvicorn main_manager:app --host 0.0.0.0 --port 80"
    );

    new cdk.CfnOutput(this, "InstanceTwoPublicIp", {
      value: ec2Instance_2.instancePublicIp,
    });
  }
}
