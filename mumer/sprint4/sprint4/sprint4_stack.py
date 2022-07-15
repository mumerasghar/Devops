from signal import alarm
from weakref import proxy
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
    aws_codedeploy as codedeploy_,
    aws_apigateway as gateway_,
)
import resources.constants as constants
from constructs import Construct


class Sprint4Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = self.create_table("Lambda_Alarm_logs", "id")
        table.apply_removal_policy(RemovalPolicy.DESTROY)

        # aws role for Cloudwatch and DynamoDB
        lambda_role = self.create_role()
        lambda_role.apply_removal_policy(RemovalPolicy.DESTROY)

        # Monitoring Lambda
        hw_lambda = self.create_lambda(
            "MyFirstLambda", "./resources/",
            "hw_lambda.lambda_handler", lambda_role
        )
        hw_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        hw_lambda.add_environment("TABLE_NAME", table.table_name)

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_events/Schedule.html
        schedule = events_.Schedule.cron(minute="0")

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
        hw_lambda.add_environment("TOPIC_ARN", topic.topic_arn)

        for url in constants.URLS:
            dimension = {"URL": url}

            avail_alarm = self.create_alarm(
                name=f"mumer_appMonitorAlarm_avail_{url}",
                threshold=1,
                comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
                metric=self.create_metric(
                    metric_name=constants.METRIC_AVAILABILITY,
                    namespace=constants.URL_MONITOR_NAMESPACE,
                    dimension=dimension
                )
            )
            avail_alarm.add_alarm_action(cw_actions_.SnsAction(topic))

            latency_alarm = self.create_alarm(
                name=f"mumer_appMonitorAlarm_latency_{url}",
                threshold=0.2,
                comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                metric=self.create_metric(
                    metric_name=constants.METRIC_AVAILABILITY,
                    namespace=constants.URL_MONITOR_NAMESPACE,
                    dimension=dimension
                )
            )
            latency_alarm.add_alarm_action(cw_actions_.SnsAction(topic))

        db_lambda = self.create_lambda(
            "DataInRecord",
            "./resources/",
            "dynamodb_lambda.lambda_handler",
            lambda_role
        )

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

        # Using aws inbuild metrics for monitoring.
        hw_duration = hw_lambda.metric(
            "Duration", period=Duration_.minutes(60)
        )

        hw_invocations = hw_lambda.metric(
            "Invocation", period=Duration_.minutes(60)
        )

        invocations_alarm = self.create_alarm(
            name="mumer_appHealthAlarm_invocations",
            threshold=1,
            comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
            metric=hw_invocations,
        )

        duration_alarm = self.create_alarm(
            name="mumer_appHealthAlarm_duration",
            threshold=5000,  # this is in milliseconds
            comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
            metric=hw_duration,
        )

        # used to make sure each CDK synthesis produces a different Version
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Alias.html#aws_cdk.aws_lambda.Alias
        alias = lambda_.Alias(
            self,
            "WH_LambdaAlias",
            alias_name="Prod",
            version=hw_lambda.current_version
        )

        # application deployment group configration and roll back policy.
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codedeploy/LambdaDeploymentGroup.html
        deployment_group = codedeploy_.LambdaDeploymentGroup(
            self,
            "mumer-WH-Deployment",
            alias=alias,
            alarms=[invocations_alarm, duration_alarm],
            deployment_config=codedeploy_.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE,
        )
        deployment_group.apply_removal_policy(RemovalPolicy.DESTROY)

        # lambda handler for api gateway
        rest_api_lambda = self.create_lambda(
            "Restapi-lambda", "./resources/",
            "rest_api_lambda.lambda_handler", lambda_role
        )

        # dynamodb table for urls
        url_table = self.create_table("Url_table", "id")
        url_table.apply_removal_policy(RemovalPolicy.DESTROY)

        rest_api_lambda.add_environment("TABLE_NAME", url_table.table_name)

        # constructing api gateway abstraction layer on application
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/LambdaRestApi.html
        gateway_api = gateway_.LambdaRestApi(
            self, "mumer-apigateway",
            handler=rest_api_lambda,
            proxy=False,
            endpoint_configuration=gateway_.EndpointConfiguration(
                types=[
                    gateway_.EndpointType.REGIONAL
                ]
            ))

        urls = gateway_api.root.add_resource("urls")
        urls.add_method("POST")
        urls.add_method("GET")
        urls.add_method("DELETE")

        url = urls.add_resource("{url_id}")
        url.add_method("PATCH")

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

    def create_table(self, id, partion_key_name):
        return dynamodb_.Table(
            self,
            id=id,
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb_.Attribute(
                name=partion_key_name, type=dynamodb_.AttributeType.STRING
            )
        )

    def create_role(self):
        return iam_.Role(
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

    def create_metric(self, metric_name, namespace, dimension):
        return cloudwatch_.Metric(
            metric_name=metric_name,
            namespace=namespace,
            dimensions_map=dimension,
            period=Duration_.minutes(60)
        )

    def create_alarm(self, name, comparison_operator, threshold, metric):
        alarm = cloudwatch_.Alarm(
            self, name,
            comparison_operator=comparison_operator,
            threshold=threshold,
            metric=metric,
            evaluation_periods=1
        )
        alarm.apply_removal_policy(RemovalPolicy.DESTROY)
        return alarm
