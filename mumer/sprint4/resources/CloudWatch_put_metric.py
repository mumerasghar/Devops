
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

    def create_alram(
            self, name, alarm_description, metricname,
            namespace, dimensions, threshold, sns_topic_arn, period=60
    ):
        return self.client.put_metric_alarm(
            AlarmName=name,
            AlarmDescription=alarm_description,
            ActionsEnabled=True,
            AlarmActions=[sns_topic_arn],
            MetricName=metricname,
            Namespace=namespace,
            Dimensions=dimensions,
            Period=period,
            EvaluationPeriods=1,
            Threshold=threshold,
            ComparisonOperator='GreaterThanThreshold',
            Statistic='SampleCount'
        )
