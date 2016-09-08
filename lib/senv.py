#!/usr/bin/env python
import argparse
import boto3
import base64
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
kms_client = boto3.client("kms", region_name='us-east-1')
key_alias = 'alias/url-shortener'


def kms_decrypt(ciphertext):
    response = kms_client.decrypt(CiphertextBlob=base64.b64decode(ciphertext))
    return response["Plaintext"]


def kms_encrypt(plaintext):
    response = kms_client.encrypt(KeyId=key_alias, Plaintext=bytes(plaintext))
    encoded_response = base64.b64encode(response['CiphertextBlob'])
    return encoded_response


def get(table_name, key):
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'key': key})
    except ClientError as e:
        return e.response['Error']['Message']
    else:
        return kms_decrypt(response['Item']['value'])


def set(table_name, key, value):
    encrypted_value = kms_encrypt(value)
    try:
        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key={'key': key},
            UpdateExpression='SET #v = :v',
            ExpressionAttributeNames={'#v': 'value'},
            ExpressionAttributeValues={':v': encrypted_value},
            ReturnValues="ALL_NEW"
        )
    except ClientError as e:
        return e.response['Error']['Message']
    else:
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='get/set encrypted environment variables from DynamoDB table')
    parser.add_argument('--table', metavar='table', default='url-shortener-envs',
                        help='(default: url-shortener-envs)')
    group = parser.add_mutually_exclusive_group()
    group.set_defaults(mode='get')
    group.add_argument('--get', metavar='key', help='key',
                       action='store_const', dest='mode', const='get')
    group.add_argument('--set', metavar='key=value', help='key=value',
                       action='store_const', dest='mode', const='set')
    parser.add_argument('value', nargs='?')

    args = parser.parse_args()

    if args.mode == 'get' and args.value:
        response = get(args.table, args.value)
        print response
    elif args.mode == 'set' and args.value:
        try:
            key, value = args.value.split('=')
        except:
            parser.error("{} requires [key=value]".format(args.mode))
        set(args.table, key, value)
        print key + '=' + value
    else:
        parser.error("{} requires a value argument".format(args.mode))
