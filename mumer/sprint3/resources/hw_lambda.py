
import datetime
from urllib import response
import urllib3
import constants
from CloudWatch_put_metric import CloudWatchPutMetric

cw = CloudWatchPutMetric()
urls = [
    'skipq.org',
    'aws.amazon.com',
    'docs.amplify.aws',
    'www.sungardas.com'
]


def create_events(metric, url, value):
    dimension = [{'Name': 'URL', 'Value': url}]
    cw.put_data(
        constants.URL_MONITOR_NAMESPACE,
        metric,
        dimension,
        value
    )


def lambda_handler(event, context):
    print("Hello world Lmabda")

    values = {}

    for url in constants.URLS:
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
