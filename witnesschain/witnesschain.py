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

API		= "/app/tracer"
API_VERSION	= "/v1"
BASE_URL	= "https://" + SERVER + ":" + SERVER_PORT + API + API_VERSION
BASE_URL_WSS	= "wss://"   + SERVER + ":" + SERVER_PORT + API + API_VERSION

LOGIN_URL	= BASE_URL + "/login"
LOGOUT_URL	= BASE_URL + "/logout"
PRE_LOGIN_URL	= BASE_URL + "/pre-login"
TRACE_URL	= BASE_URL + "/trace"
WEBSOCKET_URL	= BASE_URL_WSS + "/websocket"

CONTENT_TYPE_JSON = {
	"content-type" : "application/json"
}

SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

class TransactionTracer:
#
	def __init__(self, args):
	#
		self.session	= None	

		self.publicKey	= args["publicKey"] 
		self.keyType	= args["keyType"]
	#

	def login (self):
	#
		s = requests.Session()

		data = json.dumps ({
			"keyType"		: self.keyType,
			"publicKey"		: self.publicKey,
			"currentlyWatching"	: "base",
		})

		r = s.post (
			url	= PRE_LOGIN_URL,
			verify	= SSL_CONTEXT.check_hostname,
			data	= data,
			headers = CONTENT_TYPE_JSON
		)

		print("\n===>",r.status_code,r.url)

		if r.status_code != 200:
			print(r,r.text)
			self.session= None
			return None


		j	= json.loads(r.text.encode())
		message	= j["result"]["message"]

		print("Got message",message)

		cookies	= s.cookies.get_dict()
		self.extra_headers= {"cookie" : ";".join(["%s=%s" %(i, j) for i, j in cookies.items()]) }
		print(self.extra_headers)

		data = json.dumps ({
			"signature" : str("0x61e71cbc2ca29fc9c185071301f1d325bcdbbcf24036797bf4263fc0d87b4d2c31dbec44d06305627bc0bb17dd6a56b275a94f188f6f4b5efe7016fbc68ba6e11c")
		})

		r = s.post (
			url	= LOGIN_URL,
			verify	= SSL_CONTEXT.check_hostname,
			data	= data,
			headers = CONTENT_TYPE_JSON
		)

		print("\n===>",r.status_code,r.url)

		if r.status_code != 200:
			print("GOTx",r,"<"+r.text+">",data,s.cookies.get_dict())
			self.session= None
			return None

		self.session = s

		print("xxx session",self.session)
		cookies	= s.cookies.get_dict()
		self.extra_headers= {"cookie" : ";".join(["%s=%s" %(i, j) for i, j in cookies.items()]) }
		print(self.extra_headers)

		return True
	#

	async def logout (self,websocket):
	#
		await websocket.close()

		r = self.session.post (
			url	= LOGOUT_URL,
			verify	= SSL_CONTEXT.check_hostname,
			headers	= CONTENT_TYPE_JSON
		)

		print("\n===>",r.status_code,r.url)

		if r.status_code != 200:
			print(r.text)
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
				url	= TRACE_URL,
				data	= json.dumps(req),
				headers = CONTENT_TYPE_JSON
			)
		else:
			r = requests.post (
				url	= TRACE_URL,
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

		print("about to connect ...",self.extra_headers)

		async def handle_websockets():
		#
			async with websockets.connect(WEBSOCKET_URL, extra_headers=self.extra_headers) as websocket:
			#
				print("===> Connected to websocket")
				do_ping= True
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
							msg= await websocket.recv()
							print("GOT MESSAGE===================>",msg)
					except asyncio.exceptions.TimeoutError:
						do_ping= True
						continue

					except asyncio.exceptions.CancelledError:
						do_ping= True
						continue
					except Exception as e:
						print("GOT some exception",e)
						break

					if msg== "ping" or msg== "pong":
						do_ping= False
						continue

					try:
						msg= json.loads(msg)
					except:
						print("Message was not json",msg)
						continue 

					self.handle_challenge_as_prover(msg)

			#

			print("Handing ws...")
			await handle_websockets()
	#
#

#
