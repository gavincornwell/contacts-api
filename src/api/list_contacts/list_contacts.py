import json
import logging
import os

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

        # scan dynamodb table for all results
        _logger.debug('Calling scan on table %s', TABLE_NAME)
        response = _dynamodb.scan(
            TableName=TABLE_NAME
        )
        _logger.debug('scan response: %s', response)

        # build response body and return
        body = _build_response_body(response)

        result = {
            'statusCode': 200,
            'body': json.dumps(body)
        }
        _logger.debug('Returning result: %s', result)
        return result

    except Exception as err:
        _logger.error('Failed to get items from table: %s %s', type(err), str(err))
        result = {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to retrieve items from table, see log for details'
            })
        }
        _logger.debug('Returning result: %s', result)
        return result


def _build_response_body(response):
    """Builds a dictionary representing the response body"""

    items = {
        'data': []
    }

    for item in response['Items']:
        items['data'].append(_build_contact(item))

    return items


def _build_contact(item):
    """Builds a dictionary representing a contact"""

    contact = {
        'contactId': item['contactId']['S'],
        'name': item['name']['S'],
        'telephone': item['telephone']['S']
    }

    return contact
