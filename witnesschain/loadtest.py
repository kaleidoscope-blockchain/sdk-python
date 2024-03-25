
import sys
import json
import random
import witnesschain

from locust import HttpUser, between, task

CONTENT_TYPE_JSON = {
	"content-type" : "application/json"
}

class AppUser(HttpUser):
#
	wait_time = between(5, 15)
	
	def on_start(self):
		t = witnesschain.TransactionTracer ({
			"role"		: "app",
			"keyType"	: "ethereum",
			"privateKey": "ed9f0b916c7017e4d51edac23c79f5c3cc08107993cce093761e8c52f67e861f"
		})

		t.login()
		self.cookie = t.extra_headers['cookie']
		print("GOGOOOT",self.cookie)

	@task
	def trace(self):
		transactionHash = "0x"

		for x in range (0,65):
			d = random.randint(0,16) 
			transactionHash += "01234567890abcdef"[d]

		req = {
			"requestId"		: "EEEE",
			"chainId"		: "84532",
			#"chainId"		: "11155420",
			#"chainId"		: "999",
			"transactionHash"	: transactionHash
		}

		r = self.client.post (
			url	= "https://api.witnesschain.com/tracer/v1/app/trace", 
			data	= json.dumps(req),
			headers = {
				"cookie" : self.cookie
			}
		)
#
