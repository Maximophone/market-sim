import request
import json
import argparse

URL = 'http://localhost:5000/api/v1/'
HOST = 'localhost'
PORT = 5000

class Client(object):
    def __init__(self,name):
        self.name = name
        
    def _post(self,path,data,glob=False):
        path = URL+ ("accounts/" if glob else "accounts/{}/".format(self.id)) + path
        return requests.post(path,data=json.dumps(data))
    
    def _get(self,path,glob=False):
        path = URL + ("accounts/" if glob else "accounts/{}/".format(self.id)) + path
        return requests.get(path)
    
    def open_account(self,amount):
        response = self._post('open',{"name":self.name,"amount":amount},glob=True)
        self.id = response.json().get("account_id")
        return response.json()
        
    def get_balance(self):
        response = self._get('balance'.format(self.id))
        return response.json()
    
    def add_asset(self,asset,quantity):
        response = self._post("add_asset",{"asset":asset,"quantity":quantity})
        return response

def main():
	pass


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-h','--host',default=HOST,type=str)
	parser.add_argument('-p','--port',default=PORT,type=int)
	parser.add_argument('-v','--version',default=1,type=int,help="API version")

	args = parser.parse_args()
	URL = "http://{}:{}/api/v{}/".format(args.host,args.port,args.version)

	main()