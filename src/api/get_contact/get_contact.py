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

        # get the contact ID from the resource path
        contact_id = event['pathParameters']['id']
        _logger.info('Retrieving details for contact %s...', contact_id)

        # get item from dynamo
        _logger.debug('Calling get_item on table %s for key %s', TABLE_NAME, contact_id)
        key = {
            'contactId': {
                'S': contact_id
            }
        }
        response = _dynamodb.get_item(
            TableName=TABLE_NAME,
            Key=key,
            ReturnConsumedCapacity='TOTAL'
        )
        _logger.debug('get_item response: %s', response)

        # return 404 if Item property is missing from the DB response
        if 'Item' not in response:
            result = {
                'statusCode': 404,
                'body': ''
            }
            _logger.debug('Returning result: %s', result)
            return result

        # build response body and return
        body = _build_response_body(contact_id, response)

        result = {
            'statusCode': 200,
            'body': json.dumps(body)
        }
        _logger.debug('Returning result: %s', result)
        return result

    except Exception as err:
        _logger.error('Failed to get item from table: %s %s', type(err), str(err))
        result = {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to retrieve contact from table, see log for details'
            })
        }
        _logger.debug('Returning result: %s', result)
        return result


def _build_response_body(contact_id, response):
    """Builds a dictionary representing the response body"""

    contact_details = {
        'contactId': contact_id
    }

    item = response['Item']
    if 'name' in item:
        contact_details['name'] = item['name']['S']

    if 'telephone' in item:
        contact_details['telephone'] = item['telephone']['S']

    return contact_details
