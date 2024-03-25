import random
import sys
import witnesschain

from locust import HttpUser, between, task


class AppUser(HttpUser):
#
	wait_time = between(5, 15)
	
	def on_start(self):
		pass
		
	@task
	def trace(self):
		t = witnesschain.TransactionTracer ({
			"role"		: "app",
			"keyType"	: "ethereum",
			"privateKey": "ed9f0b916c7017e4d51edac23c79f5c3cc08107993cce093761e8c52f67e861f"
		})

		t.login()

		if t.session == None:
			print("Session is null")
			sys.exit(-1)

		transactionHash = "0x"

		for x in range (0,65):
			d = random.randint(0,16) 
			transactionHash += "01234567890abcdef"[d]

		if t.session == None:
			print("Got null session")
			sys.exit(-1)

		r = t.trace ({
			"requestId"		: "EEEE",
			"chainId"		: "84532",
			#"chainId"		: "11155420",
			#"chainId"		: "999",
			"transactionHash"	: transactionHash
		})
#
