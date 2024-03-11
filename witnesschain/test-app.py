import random

import witnesschain

t = witnesschain.TransactionTracer ({
	"role"		: "app",
	"keyType"	: "ethereum",
	"publicKey"	: "0x66607777666999966472aD1BdD5425dC9Cd34376"
})

t.login()

for i in range(0,1000):
#
	transactionHash = "0x"

	for x in range (0,65):
		d = random.randint(0,16) 
		transactionHash += "01234567890abcdef"[d]

	if t.session == None:
		break

	print("\nTracing ... [",i,"]",transactionHash)

	r = t.trace ({
		"requestId"		: "EEEE",
		"chainId"		: "999",
		"transactionHash"	: transactionHash,
	})
#
