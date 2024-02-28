import asyncio

import witnesschain

async def main():
#
	t = witnesschain.TransactionTracer ({
		"role"			: "watchtower",
		"keyType"		: "ethereum",
		"publicKey"		: "0x630391b032F444cB40B3603b579064817f312353",
		"currentlyWatching"	: "11155420"
	})

	t.login()

	print("Running ...");
	await t.run()
	print("Done...");
#

if __name__ == "__main__":
	asyncio.run(main())