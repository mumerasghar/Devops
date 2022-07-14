
import boto3


class CloudWatchPutMetric():
    def __init__(self):
        self.client = boto3.client('cloudwatch')

    def put_data(self, namespace, metric_name, dimensions, value):
        response = self.client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Dimensions': dimensions,
                    'Value': value,
                },
            ]
        )
