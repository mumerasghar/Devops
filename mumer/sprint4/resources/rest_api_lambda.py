import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    print("MY LAMBDA_HANDLER IS AW")
    print(f'event: {event.keys()}')

    method = event['httpMethod']
    # logger.info(event)

    return {
        'statusCode': 200,
        'body': method
    }
