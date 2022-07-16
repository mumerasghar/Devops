import os
import datetime
from urllib import response
import boto3
import logging
import urllib3
import constants
from CloudWatch_put_metric import CloudWatchPutMetric

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cw = CloudWatchPutMetric()
table_name = os.environ["TABLE_NAME"]

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
sns_topic_arn = os.environ["TOPIC_ARN"]

def read_urls():
    response = table.scan()
    result = response["Items"]

    while "LastEvaluationKey" in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'])
        result.extend(response['Items'])

    return result


def lambda_handler(event, context):
    print("Hello world Lmabda")

    values = {}
    urls = read_urls()
    print(table_name)
    logger.info(urls)

    for ele in urls:
        url = ele['monitor_url']
        availbility = getAvailability(url)
        dimension = [{'Name': 'URL', 'Value': url}]
        responseAvail = cw.put_data(
            constants.URL_MONITOR_NAMESPACE,
            constants.METRIC_AVAILABILITY,
            dimension,
            availbility
        )

        latency = getLatency(url)
        responseLatency = cw.put_data(
            constants.URL_MONITOR_NAMESPACE,
            constants.METRIC_LATENCY,
            dimension,
            latency
        )

        values.update({
            url: {
                "availability": availbility,
                "latency": latency
            }
        })

        cw.create_alram(
            "mumer_appMonitorAlarm_avail_"+url,
            f"availability alarm for url: {url}",
            constants.METRIC_AVAILABILITY,
            constants.URL_MONITOR_NAMESPACE,
            dimensions=dimension,
            threshold=1,
            sns_topic_arn=sns_topic_arn
        )

        # latency alarm
        cw.create_alram(
            "mumer_appMonitorAlarm_latency_"+url,
            f"Latency alarm for url: {url}",
            constants.METRIC_LATENCY,
            constants.URL_MONITOR_NAMESPACE,
            dimensions=dimension,
            threshold=float(ele["threshold"]),
            sns_topic_arn=sns_topic_arn
        )

    print(values)
    return values


def getAvailability(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return 1 if response.status == 200 else 0


def getLatency(url):
    http = urllib3.PoolManager()
    before_time = datetime.datetime.now()
    response = http.request("GET", url)
    after_time = datetime.datetime.now()
    latency = after_time - before_time

    latencySec = round(latency.microseconds * .000001, 6)
    return latencySec
