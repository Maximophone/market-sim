from flask import Flask, jsonify, make_response, request
from exchange import Exchange
import argparse
import json

def main(assets):
    ex = Exchange(assets)

    # ex.open_account('max',100)

    app = Flask(__name__)

    def errorhandler(function):
        def inner(*args,**kwargs):
            try:
                return function(*args,**kwargs)
            except Exception as e:
                return make_response(jsonify({'Error': e.args}), 500)
        inner.__name__ = function.__name__
        return inner

    # @app.errorhandler(500)
    # def not_found(error):
    #     # return 'prout'
    #     return make_response(jsonify({'error': error}), 500)

    @app.route('/api/v1/accounts/<int:account_id>/balance',methods=['GET'])
    @errorhandler
    def get_balance(account_id):
        balance = ex.get_balance(account_id)
        return jsonify({'balance':balance})

    @app.route('/api/v1/accounts/<int:account_id>/assets',methods=['GET'])
    @errorhandler
    def get_assets(account_id):
        assets = ex.get_assets(account_id)
        return jsonify({'assets':assets})

    @app.route('/api/v1/accounts/open',methods=['POST'])
    @errorhandler
    def open_account():
        data = json.loads(request.data)
        name = data['name']
        amount = data['amount']
        account_id = ex.open_account(name,amount)

        return jsonify({'account_id':account_id})

    @app.route('/api/v1/accounts/<int:account_id>/close',methods=['POST'])
    @errorhandler
    def close_account(account_id):
        amount,assets = ex.close_account(account_id)

        return jsonify({"amount":amount,"assets":assets})

    @app.route('/api/v1/accounts/<int:account_id>/credit',methods=['POST'])
    @errorhandler
    def credit_account(account_id):
        data = json.loads(request.data)
        amount = data["amount"]
        ex.credit_account(account_id,amount)
        return make_response()

    @app.route('/api/v1/accounts/<int:account_id>/add_asset',methods=['POST'])
    @errorhandler
    def add_asset(account_id):
        data = json.loads(request.data)
        asset = data["asset"]
        quantity = data["quantity"]
        ex.add_asset(account_id,asset,quantity)
        return make_response()

    @app.route('/api/v1/accounts/<int:account_id>/post_order',methods=['POST'])
    @errorhandler
    def post_order(account_id):
        data = json.loads(request.data)
        asset = data["asset"]
        side = data["side"]
        price = data["price"]
        volume = data["volume"]
        success = ex.post_order(account_id,asset,side,price,volume)
        return make_response()

    @app.route('/api/v1/accounts/<int:account_id>/take_order',methods=['POST'])
    @errorhandler
    def take_order(account_id):
        data = json.loads(request.data)
        asset = data["asset"]
        side = data["side"]
        price = data["price"]
        volume = data["volume"]
        success = ex.take_order(account_id,asset,side,price,volume)
        return make_response()

    @app.route('/api/v1/books/<string:asset>',methods=['GET'])
    @errorhandler
    def get_book(asset):
        book = ex.get_book(asset)
        return jsonify(book)

    return app



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a','--assets',nargs='+')
    args = parser.parse_args()
    app = main(args.assets)
    app.run(debug=True)
