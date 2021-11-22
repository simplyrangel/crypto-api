import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
import json
from datetime import datetime

# KuCoin API docs: 
# https://docs.kucoin.com/?lang=en_US#general
class apiwrapper:
    def __init__(
        self,
        base_url="https://api.kucoin.com",
        ):
        self.base_url=base_url

    def query(
        self,
        endpoint,
        method="GET",
        ):

        # create query:
        url = "%s%s"%(self.base_url,endpoint)
        cmd = [
            "curl",
            url,
            "--header",
            "Accept: application/json",
            "--header",
            "Content-Type: application/json",
            ]

        # submit query and return answer in JSON:  
        p = Popen(cmd,stdout=PIPE,stderr=PIPE)
        stdout,stderr = p.communicate()
        return json.loads(stdout)
