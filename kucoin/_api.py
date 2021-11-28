import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
import json
from datetime import datetime

# API authentification:
import time
import hmac
import hashlib
import base64

# KuCoin API docs: 
# https://docs.kucoin.com/?lang=en_US#general
# https://support.kucoin.plus/hc/en-us/articles/900006465403-KuCoin-API-key-upgrade-operation-guide
class apiwrapper:
    def __init__(
        self,
        base_url="https://api.kucoin.com",
        ):
        self.base_url=base_url
        self.api_key_file = None

    def read_keyfile(
        self,
        api_key_file,
        ):
        self._read_api_key(api_key_file)

    def query(
        self,
        request_path,
        body="",
        method="GET",
        ):

        # create query:
        url = "%s%s"%(self.base_url,request_path)
        unauth_cmd = [
            "curl",
            url,
            "--header",
            "Accept: application/json",
            "--header",
            "Content-Type: application/json",
            ]
        auth_cmd = self._auth_commands(method,request_path,body)
        cmd = unauth_cmd + auth_cmd

        # submit query and return answer in JSON:  
        p = Popen(cmd,stdout=PIPE,stderr=PIPE)
        stdout,stderr = p.communicate()
        return json.loads(stdout)

    def _read_api_key(
        self,
        api_key_file,
        ):
        self.api_key_file=api_key_file  
        with open(self.api_key_file,"r") as of:
            self.API_KEY = of.readline().rstrip()
            self.API_SECRET = of.readline().rstrip()
            self.API_PASSPHRASE = of.readline().rstrip()

    def _auth_commands(self,method,request_path,body):
        if self.api_key_file!=None:
            api_key = self.API_KEY
            api_secret = self.API_SECRET
            api_passphrase = self.API_PASSPHRASE
            now = int(time.time() * 1000)
            str_to_sign = str(now) + method + request_path + body
            signature = base64.b64encode(
                hmac.new(
                    api_secret.encode('utf-8'),
                    str_to_sign.encode('utf-8'),
                    hashlib.sha256,
                    ).digest()
                ).decode('utf-8') #b64encode signature
            passphrase = base64.b64encode(
                hmac.new(
                    api_secret.encode('utf-8'),
                    api_passphrase.encode('utf-8'),
                    hashlib.sha256,
                    ).digest()
                ).decode('utf-8') #b64encode passphrase
            
            # create authentication commands:
            auth_cmd = [
                "--header",
                "KC-API-SIGN:%s"%signature,
                "--header",
                "KC-API-TIMESTAMP:%s"%(str(now)),
                "--header",
                "KC-API-KEY:%s"%api_key,
                "--header",
                "KC-API-PASSPHRASE:%s"%passphrase,
                "--header",
                "KC-API-KEY-VERSION:2",
                ]
        else:
            auth_cmd = []
        return auth_cmd








