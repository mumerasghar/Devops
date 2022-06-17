import aws_cdk as core
import aws_cdk.assertions as assertions

from sprint1.sprint1_stack import Sprint1Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in sprint1/sprint1_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Sprint1Stack(app, "sprint1")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
