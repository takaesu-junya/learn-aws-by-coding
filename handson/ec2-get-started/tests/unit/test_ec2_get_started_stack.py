import aws_cdk as core
import aws_cdk.assertions as assertions

from ec2_get_started.ec2_get_started_stack import Ec2GetStartedStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ec2_get_started/ec2_get_started_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Ec2GetStartedStack(app, "ec2-get-started")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
