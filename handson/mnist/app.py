from aws_cdk import (
    core,
    aws_ec2 as ec2,
)
import os

class Ec2ForDl(core.Stack):

    def __init__(self, scope: core.App, name: str, key_name: str, student_id: str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        # student_idの型変換と検証
        student_id_int = int(student_id)
        if not 0 < student_id_int < 255:
            raise ValueError("student_id は 1 から 254 の間で指定してください")

        vpc_cidr = f"10.{student_id_int}.0.0/23"

        vpc = ec2.Vpc(
            self, f"Ec2ForDl-Vpc-{student_id_int}",
            max_azs=1,
            cidr=vpc_cidr,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"public-{student_id_int}",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        sg = ec2.SecurityGroup(
            self, f"Ec2ForDl-Sg-{student_id_int}",
            vpc=vpc,
            allow_all_outbound=True,
            security_group_name=f"dl-sg-{student_id_int}"
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
        )

        host = ec2.Instance(
            self, f"Ec2ForDl-Instance-{student_id_int}",
            instance_type=ec2.InstanceType("g4dn.xlarge"),
            machine_image=ec2.MachineImage.generic_linux({
                "us-west-2": "ami-0cd93f20c1d6006a4"
            }),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            key_name=key_name,
            instance_name=f"dl-{student_id_int}"
        )

        # Outputs
        core.CfnOutput(self, f"InstancePublicDnsName-{student_id_int}", 
                      value=host.instance_public_dns_name)
        core.CfnOutput(self, f"InstancePublicIp-{student_id_int}", 
                      value=host.instance_public_ip)

app = core.App()
Ec2ForDl(
    app, "Ec2ForDl",
    key_name=app.node.try_get_context("key_name"),
    student_id=app.node.try_get_context("student_id"),
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    }
)

app.synth()