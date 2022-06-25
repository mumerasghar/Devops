from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    RemovalPolicy,
    aws_events as events_,
    aws_events_targets as target_,
    aws_cloudwatch as cloudwatch_,
    Duration as Duration_,
    aws_iam as iam_,
    aws_sns as sns_,
    aws_cloudwatch_actions as cw_actions_,
    aws_sns_subscriptions as subscriptions_,
    aws_dynamodb as dynamodb_,
)
import resources.constants as constants
from constructs import Construct


class Sprint2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # aws role for Cloudwatch and DynamoDB
        lambda_role = iam_.Role(
            self,
            "Role",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchFullAccess"
                ),
                iam_.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonDynamoDBFullAccess"
                )
            ]
        )
        lambda_role.apply_removal_policy(RemovalPolicy.DESTROY)

        # Monitoring Lambda
        hw_lambda = self.create_lambda(
            "MyFirstLambda",
            "./resources/",
            "hw_lambda.lambda_handler",
            lambda_role
        )
        hw_lambda.apply_removal_policy(RemovalPolicy.DESTROY)

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_events/Schedule.html
        schedule = events_.Schedule.cron(minute="0/1")

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_events_targets/LambdaFunction.html
        target = target_.LambdaFunction(
            handler=hw_lambda,
        )

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_events/Rule.html
        rule = events_.Rule(
            self,
            "LambdaEventRule",
            description="this is my rule to generate auto events for my WH lambda",
            schedule=schedule,
            targets=[target],
        )
        rule.apply_removal_policy(RemovalPolicy.DESTROY)

        # creating aws topic, where we can publish events
        topic = sns_.Topic(
            self,
            "AlarmNotification"
        )
        topic.apply_removal_policy(RemovalPolicy.DESTROY)

        for url in constants.URLS:
            dimension = {"URL": url}

            availAlarm = self.create_avail_alarm(url, dimension)
            availAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
            availAlarm.add_alarm_action(cw_actions_.SnsAction(topic))

            latencyAlarm = self.create_latency_alarm(url, dimension)
            latencyAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
            latencyAlarm.add_alarm_action(cw_actions_.SnsAction(topic))

        db_lambda = self.create_lambda(
            "DataInRecord",
            "./resources/",
            "dynamodb_lambda.lambda_handler",
            lambda_role
        )

        table = self.create_table()

        db_lambda.add_environment("TABLE_NAME", table.table_name)

        # DB Lambda Subscription to SNS Topic
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sns_subscriptions/LambdaSubscription.html
        topic.add_subscription(
            subscriptions_.LambdaSubscription(
                db_lambda
            )
        )

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sns_subscriptions/EmailSubscription.html
        topic.add_subscription(
            subscriptions_.EmailSubscription(
                "muhammad.umer.skipq@gmail.com"
            )
        )

    def create_lambda(self, _id, _path, _handler, _role):
        return lambda_.Function(
            self,
            _id,
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler=_handler,
            code=lambda_.Code.from_asset(_path),
            role=_role,
            timeout=Duration_.seconds(15)
        )

    def create_table(self):
        return dynamodb_.Table(
            self,
            id="Lambda_Alarm_logs",
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            )
        )

    def create_avail_alarm(self, url, dimension):
        availalMetric_1 = cloudwatch_.Metric(
            metric_name=constants.METRIC_AVAILABILITY,
            namespace=constants.URL_MONITOR_NAMESPACE,
            dimensions_map=dimension,
            period=Duration_.minutes(1)
        )
        return cloudwatch_.Alarm(
            self,
            "Availability Alarm_"+url,
            comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
            threshold=1,
            evaluation_periods=1,
            metric=availalMetric_1
        )

    def create_latency_alarm(self, url, dimension):
        latencyMetric = cloudwatch_.Metric(
            metric_name=constants.METRIC_LATENCY,
            namespace=constants.URL_MONITOR_NAMESPACE,
            dimensions_map=dimension,
            period=Duration_.minutes(1)
        )
        return cloudwatch_.Alarm(
            self,
            "Latency Alarm_"+url,
            comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=0.2,
            evaluation_periods=1,
            metric=latencyMetric
        )
