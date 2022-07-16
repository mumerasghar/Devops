import aws_cdk as core
import aws_cdk.assertions as assertions

from sprint4.sprint4_stack import Sprint4Stack
import pytest

@pytest.fixture
def template():
    app = core.App()
    stack = Sprint4Stack(app, "sprint4")
    template = assertions.Template.from_stack(stack)
    return template


def test_lambda_queue_created(template):
    template.resource_count_is("AWS::Lambda::Function", 3)


def test_lambda_scheduler(template):
    template.find_resources("AWS::Events::Rule")


def test_sns(template):
    template.find_resources("AWS::SNS::Topic")
    template.resource_count_is("AWS::SNS::Topic", 1)


def test_alarms(template):
    template.resource_count_is("AWS::CloudWatch::Alarm", 10)


def test_dynamodb(template):
    template.find_resources("AWS::DynamoDB::Table")
