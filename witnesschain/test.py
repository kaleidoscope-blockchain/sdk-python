import witnesschain

t = witnesschain.TransactionTracer ({
	"keyType"           : "ethereum",
	"publicKey"         : "0x09d8A4FFC85833066472aD1BdD5425dC9Cd34376"
})

t.login()


 
r = t.trace ({
  "requestId"       : "xyzz",
  "chainId"         : "11155420",
  "transactionHash" : "0xc5866f29a9e0f2fa2d8808592f914a2cbfdc3a0727ad8a7395075040abf6de94",
})

print(r)
