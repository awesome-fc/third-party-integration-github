# -*- coding: utf-8 -*-

import oss2
import subprocess
import os
import time
import ast
import shutil
import json
import urllib
import fc2

HELLO_WORLD = b'200 OK!\n'
fc_region = '' #fill your fc endpoint
accessKeyId = '' # fill your fc accessKeyId
accessKeySecret = '' # fill your fc accessKeySecret

# if you open the initializer feature, please implement the initializer function, as below:
# def initializer(context):
#    logger = logging.getLogger()  
#    logger.info('initializing')

def handler(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)

    request_body_str = urllib.unquote(request_body)
    request_body_str = request_body_str[8:]
    request_body_json = json.loads(request_body_str)
    print request_body_json

    branch = request_body_json.get('repository').get('default_branch')
    sshurl = request_body_json.get('repository').get('ssh_url')
    repositoryname = request_body_json.get('repository').get('name')
    print branch, sshurl, repositoryname

    #trigger another function
    client = fc2.Client(endpoint=fc_region, accessKeyID=accessKeyId, accessKeySecret=accessKeySecret)

    arg = json.dumps({'repositoryname':repositoryname, 'branch':branch, 'sshurl':sshurl}).encode('utf-8')
    print arg
    client.invoke_function('fc-github-demo', 'func2', payload=arg, headers = {'x-fc-invocation-type': 'Async'})

    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    return [HELLO_WORLD]
