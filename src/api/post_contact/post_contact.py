import json
import logging
import os
import uuid
import time
import boto3

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.WARN)
logging.getLogger('botocore').setLevel(logging.WARN)
logging.getLogger('urllib3').setLevel(logging.WARN)

# get expected environment variables
TABLE_NAME = os.getenv('TABLE_NAME')

# setup required clients
_dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    '''Lambda entry point'''

    _logger.debug('Received event: %s', event)

    # check required environment variables are set
    if not TABLE_NAME:
        result = {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Missing environment variable: TABLE_NAME'
            })
        }
        _logger.debug('Returning result: %s', result)
        return result

    try:

        # parse the request body
        body = json.loads(event['body'])

        # process required name property
        if 'name' not in body:
            result = {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing property in request body: name'
                })
            }
            _logger.debug('Returning result: %s', result)
            return result

        name = body['name']

        # process required telephone property
        if 'telephone' not in body:
            result = {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing property in request body: telephone'
                })
            }
            _logger.debug('Returning result: %s', result)
            return result

        telephone = body['telephone']

        # generate a guid for the contact
        contact_id = uuid.uuid4()

        # add item to dynamo
        db_item = {
            'contactId': { 'S': str(contact_id) },
            'name': { 'S': name },
            'telephone': { 'S': telephone },
        }

        _logger.debug('Calling put_item on table %s with %s', TABLE_NAME, db_item)
        response = _dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=db_item,
            ReturnConsumedCapacity='TOTAL'
        )
        _logger.debug('put_item response: %s', response)

        # build response body and return
        result_item = {
            'contactId': str(contact_id),
            'name': name,
            'telephone': telephone
        }
        result = {
            'statusCode': 201,
            'body': json.dumps(result_item)
        }
        _logger.debug('Returning result: %s', result)
        return result

    except Exception as err:
        _logger.error('Failed to add item to table: %s %s', type(err), str(err))
        result = {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to add item to table, see log for details'
            })
        }
        _logger.debug('Returning result: %s', result)
        return result
