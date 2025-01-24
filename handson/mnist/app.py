#!/usr/bin/env python3
import os

import aws_cdk as cdk

from ec2_get_started.ec2_get_started_stack import Ec2GetStartedStack



app = cdk.App()

# コンテキストからkey_nameを取得する方法
key_pair = app.node.try_get_context("key_name")
if not key_pair:
    raise ValueError("key_name must be specified in context")

Ec2GetStartedStack(
    app,
    "Ec2GetStartedStack",
    key_pair=key_pair,
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    # cdk doctorコマンドで、使用されるアカウントとリージョンを確認できる
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()
