import os
import ssl
import sys
import json
import math
import time
import random
import socket
import select
import asyncio
import pathlib
import requests
import subprocess
import websockets
import websockets.client
import subprocess
import async_timeout
from calendar import timegm

HOME		= os.path.expanduser("~")

SERVER		= "api.witnesschain.com"
SERVER_PORT	= "443"

API		= "/<role>/tracer"
API_VERSION	= "/v1"
BASE_URL	= "https://" + SERVER + ":" + SERVER_PORT + API + API_VERSION
BASE_URL_WSS	= "wss://"   + SERVER + ":" + SERVER_PORT + API + API_VERSION

LOGIN_URL	= BASE_URL + "/login"
LOGOUT_URL	= BASE_URL + "/logout"
PRE_LOGIN_URL	= BASE_URL + "/pre-login"
TRACE_URL	= BASE_URL + "/trace"
WEBSOCKET_URL	= BASE_URL_WSS + "/websocket"

USER_INFO_URL	= "https://" + SERVER + ":" + SERVER_PORT + "/all/general/v1/user-info" 

CONTENT_TYPE_JSON = {
	"content-type" : "application/json"
}

SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

class TransactionTracer:
#
	def __init__(self, args):
	#
		self.session		= None	
		self.websocket		= None

		self.role		= args["role"] 
		self.publicKey		= args["publicKey"] 
		self.keyType		= args["keyType"]
		self.currentlyWatching	= "-"

		if self.role == "watchtower":
			self.currentlyWatching = args["currentlyWatching"]
	#

	def login (self):
	#
		s = requests.Session()

		data = json.dumps ({
			"keyType"		: self.keyType,
			"publicKey"		: self.publicKey,
			"currentlyWatching"	: self.currentlyWatching,
		})

		r = s.post (
			url	= PRE_LOGIN_URL.replace("<role>",self.role),
			verify	= SSL_CONTEXT.check_hostname,
			data	= data,
			headers = CONTENT_TYPE_JSON
		)

		print("\n===>",r.status_code,r.url)

		if r.status_code != 200:
			print("\n===>",r.status_code,r.url)
			self.session= None
			return None


		j	= json.loads(r.text.encode())
		message	= j["result"]["message"]

		cookies	= s.cookies.get_dict()
		self.extra_headers = {"cookie" : ";".join(["%s=%s" %(i, j) for i, j in cookies.items()]) }
		print("Cookies",r.url,self.extra_headers)

		data = json.dumps ({
			"signature" : str("0x61e71cbc2ca29fc9c185071301f1d325bcdbbcf24036797bf4263fc0d87b4d2c31dbec44d06305627bc0bb17dd6a56b275a94f188f6f4b5efe7016fbc68ba6e11c")
		})

		r = s.post (
			url	= LOGIN_URL.replace("<role>",self.role),
			verify	= SSL_CONTEXT.check_hostname,
			data	= data,
			headers = CONTENT_TYPE_JSON
		)

		print("\n===>",r.status_code,r.url)

		if r.status_code != 200:
			print("\n===>",r.status_code,r.url)
			self.session= None
			return None
		cookies	= s.cookies.get_dict()
		self.extra_headers = {"cookie" : ";".join(["%s=%s" %(i, j) for i, j in cookies.items()]) }
		print("Cookies",r.url,self.extra_headers)


		#"""
		r = s.post (
			url	= USER_INFO_URL,
			verify	=
 SSL_CONTEXT.check_hostname,
			data	= data,
			headers = CONTENT_TYPE_JSON
		)

		cookies	= s.cookies.get_dict()
		self.extra_headers = {"cookie" : ";".join(["%s=%s" %(i, j) for i, j in cookies.items()]) }
		print("Cookies",r.url,self.extra_headers)

		print("\n===>",r.status_code,r.url,r.text)

		if r.status_code != 200:
			print("\n===>",r.status_code,r.url)
			self.session= None
			return None
		#"""

		self.session = s

		cookies	= s.cookies.get_dict()
		self.extra_headers = {"cookie" : ";".join(["%s=%s" %(i, j) for i, j in cookies.items()]) }

		print(self.extra_headers)
		return True
	#

	async def logout (self,websocket):
	#
		await websocket.close()

		r = self.session.post (
			url	= LOGOUT_URL.replace("<role>",self.role),
			verify	= SSL_CONTEXT.check_hostname,
			headers	= CONTENT_TYPE_JSON
		)

		print("\n===>",r.status_code,r.url)

		if r.status_code != 200:
			print("\n===>",r.status_code,r.url)
			self.session= None
			return None

		return True
	#

	def trace(self,req):
	#
		print("session",self.session)
		r = None
		if self.session:
			r = self.session.post (
				url	= TRACE_URL.replace("<role>",self.role),
				data	= json.dumps(req),
				headers = CONTENT_TYPE_JSON
			)
		else:
			r = requests.post (
				url	= TRACE_URL.replace("<role>",self.role),
				data	= json.dumps(req),
				headers = CONTENT_TYPE_JSON
			)

		if r.status_code != 200:
			print("\n===>",r.status_code,r.url)
			print(r.text)
			return None

		print("tttttttttttttttt",r.text)

		j	= json.loads(r.text.encode())
		#result	= j["result"]

		return j
	#

	async def run(self):
	#
		if not self.session:
			print("Login did not succeed")
			return

		ws_link = WEBSOCKET_URL.replace("<role>",self.role)

		print("===> About to connect to ...", ws_link)

		async def handle_websockets():
		# {
			print("Connecting to ",ws_link)
			async with websockets.connect (ws_link, extra_headers = self.extra_headers) as websocket:
			# {
				self.websocket = websocket

				print("===> Connected to websocket")
				do_ping = True
				while True:
				#
					if do_ping:
					#
						try:
							print("Sending ping ...");
							await websocket.send("ping")
							print("Sent ping ...");
						except Exception as e:
							print("Got exception ",e)
							break
					#
					msg= None

					try:
						async with async_timeout.timeout(30):
							msg = await websocket.recv()
							print("GOT MESSAGE===================>",msg)
					except asyncio.exceptions.TimeoutError:
						do_ping = True
						continue

					except asyncio.exceptions.CancelledError:
						do_ping = True
						continue
					except Exception as e:
						print("GOT some exception",e)
						break

					if msg == "ping" or msg == "pong":
						do_ping = False
						continue

					try:
						msg = json.loads(msg)
					except:
						print("Message was not json",msg)
						continue 
					
					if self.role == "app":
						await self.handle_message_as_app(msg)
					elif self.role == "watchtower":
						await self.handle_message_as_watchtower(msg)
					else: 
						assert False

			# }
		# }

		print("===> Handing ws...")
		await handle_websockets()
	#

	async def handle_message_as_watchtower (self, msg):
	#
		print("Got",msg);

		chainId		= msg["chainId"]
		requestId	= msg["requestId"]
		transactionHash	= msg["transactionHash"]

		result = json.dumps({
			"Receipt": {
				"type": "0x7e",
				"root": "0x",
				"status": "0x1",
				"cumulativeGasUsed": "0xb729",
				"logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
				"logs": [],
				"transactionHash": transactionHash,
				"contractAddress": "0x0000000000000000000000000000000000000000",
				"gasUsed": "0xb729",
				"effectiveGasPrice": "0x0",
				"depositNonce": "0x7c216a",
				"depositReceiptVersion": "0x1",
				"blockHash": "0x477d8934cae2daa6b0d72c578dca214513f8837ddf6132ba10ec3ad94ff844ba",
				"blockNumber": "0x7c216b",
				"transactionIndex": "0x0"
			},
		})

		await self.websocket.send (
			json.dumps ({
				"api"			: "trace-transaction-response",
				"requestId"		: requestId,
				"chainId"		: chainId,
				"transactionHash"	: transactionHash,
				"result"		: result,
				"signature"		: "test-signature"
			})
		)

		try:
			async with async_timeout.timeout(30):
				response = await self.websocket.recv()
				print("GOT RESPONSE",response)
		except Exception as e:
			print("GOT some exception",e)

	#
#
