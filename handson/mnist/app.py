from aws_cdk import (
    core,
    aws_ec2 as ec2,
)
import os

class Ec2ForDl(core.Stack):
    """
    デプロイコマンド: 
        cdk deploy -c key_name=$KEY_NAME -c student_id=$STUDENT_ID
    引数:
        key_name: perman-aws-vault で取得した認証情報に含まれる社員番号
        student_id: 1 から 254 の間で指定(IPアドレスの一部に利用)
    """

    def __init__(self, scope: core.App, name: str, key_name: str, student_id: str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        if not 0 < int(student_id) < 255:
            raise ValueError("student_id は 1 から 254 の間で指定してください")

        vpc_cidr = f"10.{student_id}.0.0/23"

        vpc = ec2.Vpc(
            self, f"Ec2ForDl-Vpc-{student_id}",
            max_azs=1,
            cidr=vpc_cidr,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"public-{student_id}",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        sg = ec2.SecurityGroup(
            self, f"Ec2ForDl-Sg-{student_id}",
            vpc=vpc,
            allow_all_outbound=True,
            security_group_name=f"dl-sg-{student_id}"
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
        )

        host = ec2.Instance(
            self, f"Ec2ForDl-Instance-{student_id}",
            instance_type=ec2.InstanceType("g4dn.xlarge"),
            machine_image=ec2.MachineImage.generic_linux({
                "us-west-2": "ami-0cd93f20c1d6006a4"
            }),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            key_name=key_name,
            instance_name=f"dl-{student_id}"
        )

        # Outputs
        core.CfnOutput(self, f"InstancePublicDnsName-{student_id}", 
                      value=host.instance_public_dns_name)
        core.CfnOutput(self, f"InstancePublicIp-{student_id}", 
                      value=host.instance_public_ip)

app = core.App()
Ec2ForDl(
    app, f"Ec2ForDl{app.node.try_get_context('student_id')}",
    key_name=app.node.try_get_context("key_name"),
    student_id=app.node.try_get_context("student_id"),
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    }
)

app.synth()