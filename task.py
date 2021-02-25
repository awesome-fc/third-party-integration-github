# -*- coding: utf-8 -*-
import oss2
import subprocess
import os
import time
import ast
import shutil
import json
import urllib

endpoint = '' # fill your oss endpoint
bucketname = '' # fill your oss bucketname
accessKeyId = '' # fill your oss accessKeyId
accessKeySecret = '' # fill your oss accessKeySecret

def handler(event, context):
    evt = json.loads(event) 
    repositoryname = evt['repositoryname']
    branch = evt['branch']
    sshurl = evt['sshurl']

    print branch, sshurl, repositoryname
    
    auth = oss2.Auth(accessKeyId, accessKeySecret)
    bucket = oss2.Bucket(auth, endpoint, bucketname)
    bucket.get_object_to_file('id_rsa', '/tmp/id_rsa')
    bucket.get_object_to_file('my_ssh_executable.sh', '/tmp/my_ssh_executable.sh')
    subprocess.Popen(['chmod 0600 /tmp/id_rsa'], shell=True)
    subprocess.Popen(['chmod +x /tmp/my_ssh_executable.sh'], shell=True)

    print 'start donwload code'
    localpath = '/tmp/{}'.format(repositoryname)
    if os.path.exists(localpath):
        shutil.rmtree(localpath)
    gitclone = 'GIT_SSH="/tmp/my_ssh_executable.sh" git clone -b {b} {u}'.format(b=branch, u=sshurl)
    subprocess.Popen([gitclone], shell=True, cwd='/tmp')
    time.sleep(30)

    print 'start upload code to OSS'

    # upload code to OSS
    rt = subprocess.Popen(['find {localpath} -type f ! -path "{localpath}/.git/*"'.format(localpath=localpath)],
                          shell=True, stdout=subprocess.PIPE)
    files = rt.stdout.readlines()
    for f in files:
        localfile = f.replace("\n", "")
        ossfile = localfile.replace(localpath, repositoryname + '/', 1)
        print localfile, ossfile
        if os.path.isfile(localfile):
            bucket.put_object_from_file(ossfile, localfile)
    
    print 'upload code to OSS success'
    return "OK"
