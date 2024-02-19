import json
import requests

CONTENT_TYPE_JSON = {
        "content-type" : "application/json"
}

def trace(req):
#
	r = requests.post (
		url	= "https://api.witnesschain.com/app/tracer/v1/trace",
		data	= json.dumps(req),
		headers = CONTENT_TYPE_JSON
	)

	if r.status_code != 200:
		print("===>",r.status_code,r.url.split("/")[-1])
		print(r.text)
		# self.session = None
		return None


	j	= json.loads(r.text.encode())
	result	= j["result"]

	return result
#
