from asyncio import constants
import os
import logging
import json
from urllib import response
import boto3
from decimal import Decimal
from CloudWatch_put_metric import CloudWatchPutMetric
import constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)
sns_topic_arn = os.environ["TOPIC_ARN"]


class DecimalSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def buildResponse(statusCode, body=None):

    # Response of api calls.
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origion': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=DecimalSerializer)

    return response


def post_handler(event):
    # creating alarms on new url
    cw = CloudWatchPutMetric()

    # extracting data from body of post request
    body = json.loads(event["body"])
    logger.info(type(body))
    try:
        Item = {
            "id": body["id"],
            "monitor_url": body["url"],
            "threshold": body["threshold"],
        }

        response = table.put_item(
            Item=Item
        )
        dimension = [{'Name': 'URL', 'Value': body["url"]}]

        # availability alarm
        # cw.create_alram(
        #     "mumer_appMonitorAlarm_avail_"+body["url"],
        #     f"availability alarm for url: {body['url']}",
        #     constants.METRIC_AVAILABILITY,
        #     constants.URL_MONITOR_NAMESPACE,
        #     dimensions=dimension,
        #     threshold=1,
        #     sns_topic_arn=sns_topic_arn
        # )

        # # latency alarm
        # cw.create_alram(
        #     "mumer_appMonitorAlarm_latency_"+body["url"],
        #     f"Latency alarm for url: {body['url']}",
        #     constants.METRIC_LATENCY,
        #     constants.URL_MONITOR_NAMESPACE,
        #     dimensions=dimension,
        #     threshold=body["threshold"],
        #     sns_topic_arn=sns_topic_arn
        # )
        body = {
            "Status": "Success",
            "Item": Item
        }
        return buildResponse(200, body)
    except Exception as e:
        logger.exception("Error while inserting url in dynamodb")
        logger.exception(e)


def get_handler(event):

    # accessing query String parameters for Get operation
    parameters = event['queryStringParameters']

    try:
        response = table.get_item(
            Key={
                "id": parameters["id"]
            }
        )

        logger.info(type(response["Item"]))
        logger.info(response["Item"])
        body = {
            "Status": "Success",
            "Response": response["Item"]
        }

        return buildResponse(200, body)
    except:
        logger.exception("Error while retrieving values from dynamobd")


def patch_handler(event):
    path_parameters = event['pathParameters']
    body = json.loads(event["body"])
    try:
        logger.info(body)
        if body['url'] is not None:
            table.update_item(
                Key={'id': path_parameters["url_id"]},
                UpdateExpression='SET monitor_url = :val1',
                ExpressionAttributeValues={':val1': body['url']},
                ReturnValues="UPDATED_NEW"
            )

        if body['threshold'] is not None:
            table.update_item(
                Key={'id': path_parameters["url_id"]},
                UpdateExpression='SET threshold = :val1',
                ExpressionAttributeValues={':val1': body['threshold']},
                ReturnValues="UPDATED_NEW"
            )

        body = {
            "Status": "Success",
            "Response": table.get_item(
                Key={"id": path_parameters["url_id"]}
            )
        }

        return buildResponse(200, body)
    except:
        logger.exception("Error updating values in dynamoDb")


def delete_handler(event):
    # accessing query String parameters for Get operation
    parameters = event['queryStringParameters']
    logger.info(type(parameters))
    logger.info(parameters)
    try:
        response = table.delete_item(
            Key={
                "id": parameters["id"]
            },
            ReturnValues="ALL_OLD"
        )

        body = {
            "Status": "Success",
            "Response": response
        }

        return buildResponse(200, body)
    except:
        logger.exception("Error while retrieving values from dynamobd")


def lambda_handler(event, context):

    mapper = {
        "POST": post_handler,
        "GET": get_handler,
        "PATCH":  patch_handler,
        "DELETE": delete_handler
    }

    logger.info(event)

    http_method = event["httpMethod"]
    body = event['body']

    return mapper[http_method](event)
