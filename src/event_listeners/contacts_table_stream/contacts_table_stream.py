import os
import logging
import boto3

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.WARN)
logging.getLogger('botocore').setLevel(logging.WARN)
logging.getLogger('urllib3').setLevel(logging.WARN)


def lambda_handler(event, context):
    """Lambda entry point"""

    _logger.debug('Received event: %s', event)

    try:
        entries = []

        # iterate through the events
        for db_event in event['Records']:
            # all events should be from dynamodb but check to be sure
            if db_event['eventSource'] == 'aws:dynamodb':
                if db_event['eventName'] == 'INSERT':
                    _logger.info('Contact %s created', db_event['dynamodb']['NewImage']['contactId']['S'])
                elif db_event['eventName'] == 'MODIFY':
                    _logger.info('Contact %s updated', db_event['dynamodb']['NewImage']['contactId']['S'])
                elif db_event['eventName'] == 'REMOVE':
                    _logger.info('Contact %s deleted', db_event['dynamodb']['OldImage']['contactId']['S'])
            else:
                _logger.warning('Received event from unknown source: %s', db_event['eventSource'])

    except Exception as err:
        _logger.error('Failed to process event(s): %s', event)
        raise err

    # return empty object
    return {}
