#!/usr/bin/env python
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb", region_name='us-east-1')


def get_url_token(table_name, key, value):
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(
            Key={
                key: value
            }
        )
    except ClientError as e:
        return e.response['Error']['Message']
    else:
        return response


def create_url_token(table_name, params):
    expressionAttributeValues = {
        ':p': params['destination_url'],
        ':d': params['last_updated'],
        ':u': params['updated_by'],
        ':s': 'locked'
    }
    updateExpression = 'SET destination_url = :p, last_updated = :d, updated_by = :u'

    if 'description' in params.keys():
        expressionAttributeValues[':desc'] = params['description']
        updateExpression += ', description = :desc'

    try:
        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key={
                'token': params['url_token']
            },
            UpdateExpression=updateExpression,
            ConditionExpression='#s <> :s',
            ExpressionAttributeNames={
                '#s': 'status'
            },
            ExpressionAttributeValues=expressionAttributeValues,
            ReturnValues="ALL_NEW"
        )
    except ClientError as e:
        return e.response['Error']['Message']
    else:
        return response


def scan_url_tokens(table_name, filterExpression, expressionAttributeValues, expressionAttributeNames):
    try:
        table = dynamodb.Table(table_name)
        response = table.scan(
            FilterExpression=filterExpression,
            ExpressionAttributeValues=expressionAttributeValues,
            ExpressionAttributeNames=expressionAttributeNames
        )
    except ClientError as e:
        return e.response['Error']['Message']
    else:
        return response
