import witnesschain

t = witnesschain.TransactionTracer ({
	"role"		: "app",
	"keyType"	: "ethereum",
	"publicKey"	: "0x09d8A4FFC85833066472aD1BdD5425dC9Cd34376"
})

t.login()

r = t.trace ({
	"requestId"		: "EEEE",
	"chainId"		: "11155420",
	"transactionHash"	: "0x77766f29a5e0f2fa2d8808092f914a2cbfdc3a0727ad8a7395075040cdf6de99",
})

print(r)
