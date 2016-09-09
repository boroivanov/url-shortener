#!/usr/bin/env python

"""Create and Search short URLs"""

import datetime
import uuid
import lib.dynamo as dynamo
import lib.senv as senv

from urlparse import parse_qs
import logging

tokens_table = 'url-shortener-tokens'
envs_table = 'url-shortener-envs'

expected_token = senv.get(envs_table, 'verification_token')
service_url = senv.get(envs_table, 'service_url')
service_env = senv.get(envs_table, 'service_env')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def set_url(user, command_text):
    """
    Create short URL.
    Short URLs without description are temporary
    and are not shown in search.
    """

    date = datetime.datetime
    params = {
        'url_token': uuid.uuid4().urn[9:],
        'destination_url': command_text[0],
        'updated_by': user,
        'last_updated': date.now().isoformat()
    }
    attachment_title = params['url_token']
    if len(command_text) > 1:
        params['description'] = " ".join(command_text[1:])
        attachment_title = params['description']

    response = dynamo.create_url_token(tokens_table, params)
    print 'Update item succeeded: ' + str(response)
    content = {
        'text': 'Created new short URL:',
        "attachments": [{
            "fallback": "Added " + service_url + "/" + service_env + "/" + params['url_token'],
            "color": "#36a64f",
            "title": attachment_title,
            "title_link": service_url + "/" + service_env + "/" + params['url_token'],
            "footer": "Updated by: " + user + " on " + params['last_updated'] +
            " | " + params['url_token'],
        }]
    }
    return content


def search_url(user, command_text):
    """
    Search Public and the user's URLs.
    If no search term was provided only show the user's short URLs.
    """
    command = " ".join(command_text)

    if len(command) == 0:
        search_term = user
        filterExpression = "(#u = :u)"
        expressionAttributeNames = {"#u": "updated_by"}
        expressionAttributeValues = {":u": user}
    else:
        search_term = command
        filterExpression = "(contains(#d, :s)) AND (#s = :p OR #u = :u)"
        expressionAttributeNames = {
            "#d": "description",
            "#u": "updated_by",
            "#s": "scope"
        }
        expressionAttributeValues = {
            ":s": command,
            ":u": user,
            ":p": "public"
        }
    response = dynamo.scan_url_tokens(
        tokens_table, filterExpression, expressionAttributeValues, expressionAttributeNames)

    content = {
        'text': 'Search resutls for: ' + search_term,
        'attachments': []
    }

    print str(response)
    for item in response['Items']:
        url_token = item['token']
        try:
            description = item['description']
        except:
            description = url_token
        last_updated = item['last_updated']
        updated_by = item['updated_by']
        attachment_title = description
        attachment = {
            "fallback": service_url + "/" + service_env + "/" + url_token,
            "color": "#36a64f",
            "title": attachment_title,
            "title_link": service_url + "/" + service_env + "/" + url_token,
            "footer": "Updated by: " + updated_by + " on " + last_updated + " | " + url_token
        }
        content['attachments'].append(attachment)
    print 'Found ' + str(len(content['attachments'])) + ' url tokens.'
    return content


def handler(event, context):
    req_body = event['body']
    params = parse_qs(req_body)
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match exptected", token)
        raise Exception("Invalid request token")

    user = params['user_name'][0]
    # command = params['command'][0]
    # channel = params['channel_name'][0]
    try:
        command_text = params['text'][0].split(' ')
    except:
        command_text = ['']

    if command_text[0].startswith('http://') or command_text[0].startswith('https://'):
        print 'creating url token:'
        response = set_url(user, command_text)
    else:
        print 'searching url tokens:'
        response = search_url(user, command_text)

    return response


# Local testing
if __name__ == "__main__":
    team_domain = senv.get(envs_table, 'team_domain')
    channel_id = senv.get(envs_table, 'channel_id')
    channel_name = 'test'
    user_id = senv.get(envs_table, 'user_id')
    user_name = 'boro'
    command = 'url'
    command_text = 'https://google.com+google+site+here'    # set short url
    # command_text = 'google'                                 # get short url
    response_url = senv.get(envs_table, 'response_url')

    event = {
        "body": "token=" + expected_token +
        "&team_domain=" + team_domain +
        "&channel_id=" + channel_id +
        "&channel_name=" + channel_name +
        "&user_id=" + user_id +
        "&user_name=" + user_name +
        "&command=%2F" + command +
        "&text=" + command_text +
        "&response_url=" + response_url
    }

    handler(event, None)
