# This file will contain the server that runs and takes GET and POST requests
# Created by Izak Fritz 04-09-18
# For the Stably team

from flask import Flask
from flask import jsonify
from flask import request

import bittrexWrapper

app = Flask(__name__)

# Declare an instance of a Bittrex wrapper
wrapper = bittrexWrapper.Wrapper("keys.txt")

# App route for the 'get-fill-price' api call
@app.route('/api/v1.0/get-fill-price', methods=['GET'])
def get_fill_price():
    # Check that all three arguments are present, and only three are present
    arguments = ['base-currency', 'counter-currency', 'quantity']

    if not all(args in arguments for args in request.args) or not len(request.args) == 3:
        # Invalid arguments
        return jsonify({'success': False, 'message': 'invalid arguments'})
    elif float(request.args['quantity']) < 0:
        # Invalid arguments
        return jsonify({'success': False, 'message': 'invalid quantity'})
    # Check that the market is valid
    elif not wrapper.is_valid_market(request.args['base-currency'],
                                     request.args['counter-currency']):
        # Invalid market
        return jsonify({'success': False, 'message': 'invalid market'})

    # TODO: Return fill price
    return jsonify({'success': True})

# App route for the 'get-currency-balance' api call
@app.route('/api/v1.0/get-currency-balance', methods=['GET'])
def get_currency_balance():
    arguments = ['currency']

    # Check that the argument currency is present, and that it is the only arg
    if not all(args in arguments for args in request.args) or not len(request.args) == 1:
        # Invalid arguments
        return jsonify({'success': False, 'message': 'invalid arguments'})
    # Check for valid currency
    elif not wrapper.is_valid_currency(request.args['currency']):
        return jsonify({'success': False, 'message': 'invalid currency'})

    # TODO: Retun balance
    return jsonify({'success': True})

# App route for the 'send-order' api call
@app.route('/api/v1.0/send-order', methods=['POST'])
def send_order():
    arguments = ['base-currency', 'counter-currency', 'order-type', 'amount']

    # Check that all four arguments are present, and only three are present
    if not all(args in arguments for args in request.form) or not len(request.form) == 4:
        return jsonify({'success': False, 'message': 'invalid arguments'})
    # Check for valid amount
    elif float(request.form['amount']) < 0:
        return jsonify({'success': False, 'message': 'invalid amount'})
    # Check for valid market
    elif not wrapper.is_valid_market(request.form['base-currency'],
                                     request.form['counter-currency']):
        return jsonify({'success': False, 'message': 'invalid market'})
    # Check for valid order-type
    elif not (request.form['order-type'] == 'buy' or request.form['order-type'] == 'sell'):
        return jsonify({'success': False, 'message': 'invalid order-type'})

    # TODO: Send order
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run()
