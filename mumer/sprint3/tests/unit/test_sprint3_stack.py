import aws_cdk as core
import aws_cdk.assertions as assertions

from sprint3.sprint3_stack import Sprint3Stack
import pytest
# example tests. To run these tests, uncomment this file along with the example
# resource in sprint3/sprint3_stack.py


# def test_sqs_queue_created():
#     app = core.App()
#     stack = Sprint3Stack(app, "sprint3")
#     template = assertions.Template.from_stack(stack)

# #     template.has_resource_properties("AWS::SQS::Queue", {
# #         "VisibilityTimeout": 300
# #     })

@pytest.fixture
def template():
    app = core.App()
    stack = Sprint3Stack(app, "sprint3")
    template = assertions.Template.from_stack(stack)
    return template


def test_lambda_queue_created(template):
    template.resource_count_is("AWS::Lambda::Function", 2)


def test_lambda_scheduler(template):
    template.find_resources("AWS::Events::Rule")


def test_sns(template):
    template.find_resources("AWS::SNS::Topic")
    template.resource_count_is("AWS::SNS::Topic", 1)


def test_alarms(template):
    template.resource_count_is("AWS::CloudWatch::Alarm", 10)


def test_dynamodb(template):
    template.find_resources("AWS::DynamoDB::Table")
