from importlib.resources import path
from aws_cdk import (
    Stack,
    aws_lambda as lambda_
)
from constructs import Construct


class Sprint1Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        hw_lambda = self.create_lambda(
            "MyFirstLambda",
            "./resources/",
            "hw_lambda.lambda_handler"
        )

        # example resource
        # queue = sqs.Queue(
        #     self, "Sprint1Queue",
        #     visibility_timeout=Duration.seconds(300),
        # )

    def create_lambda(self, _id, _path, _handler):
        return lambda_.Function(
            self,
            _id,
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler=_handler,
            code=lambda_.Code.from_asset(_path)
        )
