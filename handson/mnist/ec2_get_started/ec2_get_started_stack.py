from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    # aws_sqs as sqs,
)
from constructs import Construct

class Ec2GetStartedStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, key_pair: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # <1>
        vpc = ec2.Vpc(
            self,
            "Takaesu-Vpc",
            max_azs=1,
            ip_addresses=ec2.IpAddresses.cidr("10.10.0.0/26"), # 64アドレス
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        # <2>
        sg = ec2.SecurityGroup(
            self,
            "Takaesu-Sg",
            vpc=vpc,
            allow_all_outbound=True,
        )

        # <3>
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(), # 0.0.0.0/0 で全てのIPアドレスからのアクセスを許可
            # 特定のIP範囲のみ
            # peer=ec2.Peer.ipv4('10.0.0.0/16')
            # 特定のIPアドレス
            # ec2.Peer.ipv4('203.0.113.1/32')
            # 別のセキュリティグループ
            # ec2.Peer.security_group_id('sg-1234567890abcdef0')
            # 別のセキュリティグループ（参照渡し）
            # ec2.Peer.security_group(another_security_group)

            connection=ec2.Port.tcp(22),
            # HTTP なら
            # connection=ec2.Port.tcp(80),
        )

        # <4>
        host = ec2.Instance(
            self,
            id="Takaesu-EC2-Instance",
            instance_name="Takaesu-EC2-Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            # key_name=key_pair
            key_pair=ec2.KeyPair.from_key_pair_name(self, "Takaesu-Key-Pair", key_pair)
        )