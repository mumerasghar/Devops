import datetime
import urllib3
import boto3
import os
import constants as constants
import json
from pathlib import Path
from CloudWatch_put_metric import CloudWatchPutMetric
from dynamodb import DynamoDb

# To create boto3 dynamodb resource
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):

    watch = CloudWatchPutMetric()
    db = DynamoDb()

    values = dict()
    table_name = os.environ["TABLE_NAME"]
    sns_topic_arn = os.environ["TOPIC_ARN"]

    result = db.read_db(table_name)

    print(result)
    lists_of_urls = result

    for item in result:

        avail = get_availability(item["monitor_url"])
        latency = get_latency(item["monitor_url"])

        values.update({
            item["monitor_url"]: {
                'availability': avail,
                'latency': latency
            }
        })

        threshold = float(item["threshold"])

        dimensions = [
            {
                "Name": "URL",
                "Value": item["monitor_url"]
            },
            {
                "Name": "Region",
                "Value": constants.Region
            }]

        watch.put_data(constants.Name_Space,
                       constants.Metric_Availability, dimensions, avail)
        watch.put_data(constants.Name_Space,
                       constants.Metric_Latency, dimensions, latency)

        watch.create_alram(item["monitor_url"] + "-Latency Alarm",
                           "Latency Alarm for" + item["monitor_url"],
                           constants.METRIC_LATENCY,
                           constants.URL_MONITOR_NAMESPACE,
                           dimensions,
                           threshold,
                           sns_topic_arn,
                           period=60)
        print(values)
    return values


def get_availability(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    if response.status == 200:
        return 1.0
    else:
        return 0.0


def get_latency(url):
    http = urllib3.PoolManager()
    start = datetime.datetime.now()
    response = http.request("GET", url)
    end = datetime.datetime.now()
    delta = end-start
    latency_sec = round(delta.microseconds * 0.000001, 6)
    return latency_sec
