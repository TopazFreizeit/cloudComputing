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

    // import default VPC
    const vpc = ec2.Vpc.fromLookup(this, "my-default-vpc", {
      isDefault: true,
    });

    // create a security group for the EC2 instance
    const webserver_and_redis_SG = new ec2.SecurityGroup(
      this,
      "webserver-and-redis-SG",
      {
        vpc: vpc,
        securityGroupName: "webserver-and-redis-SG",
      }
    );

    webserver_and_redis_SG.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(6379),
      "allow 6379 traffic from anywhere"
    );

    webserver_and_redis_SG.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(8080),
      "allow HTTP traffic from anywhere"
    );

    // IAM role that allow full access to EC2
    const role = new Role(this, "InstanceRole", {
      assumedBy: new ServicePrincipal("ec2.amazonaws.com"),
    });

    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonEC2FullAccess")
    );

    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName("IAMFullAccess")
    );

    const ec2Instance_1 = new ec2.Instance(this, "endpoint-instance-1", {
      vpc: vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      securityGroup: webserver_and_redis_SG,
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

    const ec2Instance_2 = new ec2.Instance(this, "endpoint-instance-2", {
      vpc: vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      securityGroup: webserver_and_redis_SG,
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

    const ec2Instance_redis = new ec2.Instance(this, "redis-instance", {
      vpc: vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      securityGroup: webserver_and_redis_SG,
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

    // const ec2Instance_worker = new ec2.Instance(this, "worker-instance", {
    //   vpc: vpc,
    //   vpcSubnets: {
    //     subnetType: ec2.SubnetType.PUBLIC,
    //   },
    //   securityGroup: webserver_and_redis_SG,
    //   instanceType: ec2.InstanceType.of(
    //     ec2.InstanceClass.T2,
    //     ec2.InstanceSize.MICRO
    //   ),
    //   machineImage: new ec2.AmazonLinuxImage({
    //     generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
    //   }),
    //   userData: ec2.UserData.forLinux({ shebang: "#!/bin/bash" }),
    //   role: role,
    // });

    const redisInstanceUserData = `
      yum update -y
      yum install docker -y
      service docker start
      usermod -a -G docker ec2-user
      docker pull redis
      docker run -d -p 6379:6379 --name redis-container redis
      docker run --name redis-commander -p 8080:8081 -e REDIS_HOSTS=localhost:6379 rediscommander/redis-commander
     `;

    ec2Instance_redis.addUserData(redisInstanceUserData);

    const ec2InstanceUserData = `
      yum update -y
      yum install -y git
      yum install -y python3
      yum install -y python3-pip
      pip3 install urllib3==1.26.6  boto3
      pip3 install redis
      pip3 install fastapi
      pip3 install requests
      pip3 install "uvicorn[standard]"
      git clone https://github.com/TopazFreizeit/cloudComputing.git
      cd cloudComputing
      cd src
      uvicorn main_facade:app --host 0.0.0.0 --port 8080
     `;

    ec2Instance_1.addUserData(ec2InstanceUserData);
    ec2Instance_2.addUserData(ec2InstanceUserData);

    // const ec2InstanceWorkerUserData = `
    //   #!/bin/bash
    //   yum update -y
    //   yum install -y git
    //   yum install -y python3
    //   yum install -y python3-pip
    //   pip3 install "uvicorn[standard]" fastapi boto3 redis
    //   git clone https://github.com/TopazFreizeit/cloudComputing.git
    //   cd cloudComputing
    //   cd src
    //   python3 worker.py
    //  `;

    // ec2Instance_worker.addUserData(ec2InstanceWorkerUserData);

    new cdk.CfnOutput(this, "InstanceOnePublicIp", {
      value: ec2Instance_1.instancePublicIp,
    });

    new cdk.CfnOutput(this, "InstanceTwoPublicIp", {
      value: ec2Instance_2.instancePublicIp,
    });
  }
}
