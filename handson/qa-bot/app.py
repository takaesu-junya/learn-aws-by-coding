from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_dynamodb as dynamodb,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_logs,
    aws_ecr_assets as ecr_assets
)
import os

class EcsClusterQaBot(core.Stack):
    """
    デプロイコマンド: 
        cdk deploy -c key_name=$KEY_NAME -c student_id=$STUDENT_ID
    引数:
        key_name: perman-aws-vault で取得した認証情報に含まれる社員番号
        student_id: 1 から 254 の間で指定(IPアドレスの一部に利用)
    """

    def __init__(self, scope: core.App, name: str, student_id: str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        if not 0 < int(student_id) < 255:
            raise ValueError("student_id は 1 から 254 の間で指定してください")

        # <1>
        # dynamoDB table to store questions and answers
        table = dynamodb.Table(
            # CDKの論理ID - スタック内でリソースを一意に識別するための名前
            self, f"EcsClusterQaBot-Table-{student_id}",
            partition_key=dynamodb.Attribute(
                # パーティションキーの名前 - テーブルの各項目を一意に識別するための主キー
                name="item_id",
                # パーティションキーのデータ型 - 文字列型を指定
                type=dynamodb.AttributeType.STRING
            ),
            # 請求モード - リクエスト数に応じた課金方式(オンデマンドキャパシティ)
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            # 削除ポリシー - CDKスタック削除時にテーブルも完全に削除する設定
            removal_policy=core.RemovalPolicy.DESTROY,
            # 実際のAWS上でのテーブル名 - student_idを含めて一意性を確保
            table_name=f"qabot-table-{student_id}"
        )

        # <2>
        vpc = ec2.Vpc(
            self, f"EcsClusterQaBot-Vpc-{student_id}",
            max_azs=1,
            cidr=f"10.{student_id}.0.0/23",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"public-{student_id}",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        # <3>
        cluster = ecs.Cluster(
            self, f"EcsClusterQaBot-Cluster-{student_id}",
            vpc=vpc,
            cluster_name=f"qabot-cluster-{student_id}"
        )

        # <4>
        taskdef = ecs.FargateTaskDefinition(
            self, f"EcsClusterQaBot-TaskDef-{student_id}",
            cpu=1024,
            memory_limit_mib=4096,
            family=f"qabot-task-{student_id}"
        )

        taskdef.add_to_execution_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ],
                resources=["*"]
            )
        )

        # grant permissions
        table.grant_read_write_data(taskdef.task_role)
        taskdef.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["ssm:GetParameter"]
            )
        )

        # <5>
        container = taskdef.add_container(
            f"EcsClusterQaBot-Container-{student_id}",
            image=ecs.ContainerImage.from_registry(
                "101313435800.dkr.ecr.us-west-2.amazonaws.com/takaesu-qabot:latest"
            ),
            environment={
                "STUDENT_ID": student_id
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=f"EcsClusterQaBot-{student_id}",
                log_retention=aws_logs.RetentionDays.ONE_DAY
            ),
        )

        # Store parameters in SSM
        ssm.StringParameter(
            self, f"ECS_CLUSTER_NAME_{student_id}",
            parameter_name=f"/qabot/{student_id}/ECS_CLUSTER_NAME",
            string_value=cluster.cluster_name,
        )
        ssm.StringParameter(
            self, f"ECS_TASK_DEFINITION_ARN_{student_id}",
            parameter_name=f"/qabot/{student_id}/ECS_TASK_DEFINITION_ARN",
            string_value=taskdef.task_definition_arn
        )
        ssm.StringParameter(
            self, f"ECS_TASK_VPC_SUBNET_1_{student_id}",
            parameter_name=f"/qabot/{student_id}/ECS_TASK_VPC_SUBNET_1",
            string_value=vpc.public_subnets[0].subnet_id
        )
        ssm.StringParameter(
            self, f"CONTAINER_NAME_{student_id}",
            parameter_name=f"/qabot/{student_id}/CONTAINER_NAME",
            string_value=container.container_name
        )
        ssm.StringParameter(
            self, f"TABLE_NAME_{student_id}",
            parameter_name=f"/qabot/{student_id}/TABLE_NAME",
            string_value=table.table_name
        )

        core.CfnOutput(self, f"ClusterName-{student_id}", value=cluster.cluster_name)
        core.CfnOutput(self, f"TaskDefinitionArn-{student_id}", value=taskdef.task_definition_arn)

app = core.App()
EcsClusterQaBot(
    app, f"EcsClusterQaBot{app.node.try_get_context('student_id')}",
    student_id=app.node.try_get_context("student_id"),
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    }
)

app.synth()
