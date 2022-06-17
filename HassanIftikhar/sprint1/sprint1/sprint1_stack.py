# from cgitb import handler
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda as lambda_
)

from constructs import Construct

class Sprint1Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        hw_lambda = self.create_lambda("First Lambda" ,"./resources", "hw_lambda.lambda_handler")
        # example resource
        # queue = sqs.Queue(
        #     self, "Sprint1Queue",
        #     visibility_timeout=Duration.seconds(300),
        # )
    def create_lambda(self, id_, path, handler):
        return lambda_.Function(self, id_,
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler=handler,
        code=lambda_.Code.from_asset(path)
)