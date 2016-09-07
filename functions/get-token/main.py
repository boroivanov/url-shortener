#!/usr/bin/env python
import lib.dynamo as dynamo

table = 'url-shortener-tokens'


def handler(event, context):
    token = event['token']
    response = dynamo.get_url_token(table, 'token', token)

    if 'Item' in response.keys() and 'destination_url' in response['Item'].keys():
        destination_url = response['Item']['destination_url']
        print 'Found token: ' + token + ' (' + destination_url + ')'
        content = '<html><body>Moved: <a href="' + destination_url + \
            '">' + destination_url + '</a></body></html>'
        return {'destination_url': destination_url, 'content': content}
    else:
        print 'Cannot find token: ' + token
        content = '<html><body><h1>Not Found</h1></body></html'
        return content

# Local testing
if __name__ == "__main__":
    event = {
        'token': 'f51kbja1o91gg97np09mf9qirn62ob7f'
    }
    handler(event, None)
