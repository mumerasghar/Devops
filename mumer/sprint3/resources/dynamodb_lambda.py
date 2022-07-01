
import os
from urllib import response
import boto3
import uuid


def lambda_handler(event, context):
    # DynameDB table name
    table_name = os.environ.get('TABLE_NAME')

    # DynamoDb client
    client = boto3.client('dynamodb')

    print("table_name: ", table_name)

    response = client.put_item(
        TableName=table_name,
        Item={
            'id': {
                'S': str(uuid.uuid1())
            },
            'Message': {
                'S': event['Records'][0]['Sns']['Message']
            }
        }
    )

    return response
