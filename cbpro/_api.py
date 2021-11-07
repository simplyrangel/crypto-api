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
# https://docs.pro.coinbase.com/#authentication

# write class based on work explained in:
# "coinbasepro-1 API authentification.ipynb"
class apiwrapper:
	def __init__(
		self,
		api_key_file,
		endpoint="https://api.pro.coinbase.com",
		):
		self.endpoint=endpoint
		self._read_api_key(api_key_file)

	def query(
		self,
		request_path,
		body="",
		method="GET",
		debug=False,
		):
		# generate signature:
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
		
		# create query:
		url = "%s%s"%(self.endpoint,request_path)
		cmd = [
			"curl",
			url,
			"--header",
			"Accept: application/json",
			"--header",
			"Content-Type: application/json",
			"--header",
			"CB-ACCESS-KEY: %s"%self.API_KEY,
			"--header",
			"CB-ACCESS-SIGN: %s"%signature_b64,
			"--header",
			"CB-ACCESS-TIMESTAMP: %s"%timestamp,
			"--header",
			"CB-ACCESS-PASSPHRASE: %s"%self.API_PASSPHRASE,
			]
		
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
		with open(api_key_file,"r") as of:
			self.API_KEY = of.readline().rstrip()
			self.API_SECRET = of.readline().rstrip()
			self.API_PASSPHRASE = of.readline().rstrip()
			




    





