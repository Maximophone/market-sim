from flask import Flask, jsonify, make_response, request
from exchange import Exchange
import argparse

def main(assets):
	ex = Exchange(assets)

	ex.open_account('max',100)

	app = Flask(__name__)

	@app.route('/api/v1/accounts/<int:account_id>/balance',methods=['GET'])
	def get_balance(account_id):
		return jsonify(ex.get_balance(account_id))

	@app.route('/api/v1/accounts/open',methods=['GET'])
	def open_account()

	return app



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-a','--assets',nargs='+')
	args = parser.parse_args()
	app = main(args.assets)
	app.run(debug=True)
