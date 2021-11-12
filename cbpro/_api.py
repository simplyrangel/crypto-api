import numpy as np
import pandas as pd
from subprocess import Popen, PIPE, run
import json
from datetime import datetime

# API authentification:
import time
import hmac
import hashlib
import base64

# API documentation:
# https://docs.cloud.coinbase.com/exchange/reference
class apiwrapper:
    def __init__(
        self,
        endpoint="https://api.exchange.coinbase.com",
        ):
        self.endpoint=endpoint
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
        debug=False,
        ):
        
        # create query:
        url = "%s%s"%(self.endpoint,request_path)
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
        
        # print bash curl argument if debug is True:
        if debug:
            print(" ".join(cmd))
        
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
            hmac_key = base64.b64decode(self.API_SECRET)
            timestamp = str(time.time())
            message = timestamp + method + request_path + body
            message = message.encode('ascii')
            signature = hmac.new(
                hmac_key,
                message,
                hashlib.sha256,
                )
            signature_b64 = base64.b64encode(
                signature.digest()
                ).decode('utf-8')
            
            # commands:
            auth_cmd = [
                "--header",
                "CB-ACCESS-KEY: %s"%self.API_KEY,
                "--header",
                "CB-ACCESS-SIGN: %s"%signature_b64,
                "--header",
                "CB-ACCESS-TIMESTAMP: %s"%timestamp,
                "--header",
                "CB-ACCESS-PASSPHRASE: %s"%self.API_PASSPHRASE,
                ]
        else:
            auth_cmd = []
        return auth_cmd
