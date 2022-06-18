import aws_cdk as core
import aws_cdk.assertions as assertions
from sprint1.sprint1_stack import Sprint1Stack


def test_sqs_queue_created():
    app = core.App()
    stack = Sprint1Stack(app, "sprint1")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = Sprint1Stack(app, "sprint1")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)
