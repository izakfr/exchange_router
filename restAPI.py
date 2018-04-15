# This file will contain the server that runs and takes GET and POST requests
# Created by Izak Fritz 04-09-18
# For the Stably team
import time
import threading

from flask import Flask
from flask import jsonify
from flask import request
from queue import Queue

import bittrexWrapper

# Function to get average fill price based on a Bittrex book
# Requires a Bittrex API respose for getorderbook
def get_average_fill_price(requestResponse, quantity):
    quantityToFill = quantity
    avgPrice = 0
    sumFilled = 0
    for order in requestResponse['result']:
        tempQuantity = float(order['Quantity'])
        tempPrice = float(order['Rate'])

        # If buying this order would put quantityToFill below 0, only buy part
        # of the order
        if (quantityToFill - tempQuantity < 0):
            # Update the average price and break (done with our whole order)
            avgPrice = (avgPrice * sumFilled + quantityToFill * tempPrice)
            avgPrice /= (quantityToFill + sumFilled)
            break
        else:
            # Update the average price, sumFilled, and quantityToFill
            avgPrice = (avgPrice * sumFilled + tempQuantity * tempPrice)
            avgPrice /= (tempQuantity + sumFilled)
            sumFilled += tempQuantity
            quantityToFill -= tempQuantity

    return avgPrice

# Function to calculate what our ask price should be for a sell and what our
# bid price should be for a buy. Due to the nature of limit orders, if we place
# an ask lower than the highest bid, we will get filled at that bid price.
# Therefore we place a bid/ask deep enough into the book to get fulled filled.
def get_rate(requestResponse, quantity, marketSide):
    multiplicationFactor = 1.005 if marketSide == 'buy' else .995
    quantityToFill = quantity
    sumFilled = 0
    for order in requestResponse['result']:
        tempQuantity = float(order['Quantity'])
        tempPrice = float(order['Rate'])

        if (quantityToFill - tempQuantity < 0):
            return float('%.8f'%(tempPrice * multiplicationFactor))
        else:
            quantityToFill -= tempQuantity

app = Flask(__name__)

# Thread lock for concurrent requests
exchangeLock = threading.Lock()

# Declare an instance of a Bittrex wrapper
wrapper = bittrexWrapper.Wrapper("keys.txt")

# App route for the 'get-fill-price' api call
@app.route('/api/v1.0/get-fill-price', methods=['GET'])
def get_fill_price():
    # Check that all three arguments are present, and only three are present
    arguments = ['base-currency', 'counter-currency', 'quantity']

    # Acquire exchange lock
    exchangeLock.acquire()

    # Check that the number of arguments are correct
    if not all(args in arguments for args in request.args) or not len(request.args) == 3:
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid arguments'})

    # Check for valid quantity
    if float(request.args['quantity']) < 0:
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid quantity'})

    # Check that the market is valid
    elif not wrapper.is_valid_market(request.args['base-currency'],
                                     request.args['counter-currency']):
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid market'})

    # Return fill price
    quantityToFill = float(request.args['quantity'])
    formattedTicker = wrapper.format_ticker(request.args['base-currency'],
                                            request.args['counter-currency'])
    orderbookResponse = wrapper.get_orderbook(formattedTicker, "buy")

    avgPrice = get_average_fill_price(orderbookResponse, quantityToFill)

    # Release lock and return
    exchangeLock.release()
    return jsonify({'success': True, 'fill-price': avgPrice})

# App route for the 'get-currency-balance' api call
@app.route('/api/v1.0/get-currency-balance', methods=['GET'])
def get_currency_balance():
    arguments = ['currency']

    # Acquire exchange lock
    exchangeLock.acquire()

    # Check that the argument currency is present, and that it is the only arg
    if not all(args in arguments for args in request.args) or not len(request.args) == 1:
        # Invalid arguments
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid arguments'})

    # Check for valid currency
    if not wrapper.is_valid_currency(request.args['currency']):
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid currency'})

    # Get currency balance from Bittrex
    balance = wrapper.get_balance(request.args['currency'])['result']['Balance']

    # Release lock and return
    exchangeLock.release()
    return jsonify({'success': True, 'balance': balance})

# App route for the 'send-order' api call
@app.route('/api/v1.0/send-order', methods=['POST'])
def send_order():
    arguments = ['base-currency', 'counter-currency', 'order-type', 'amount']

    # Acquire exchange lock
    exchangeLock.acquire()

    # Check that all four arguments are present, and only three are present
    if not all(args in arguments for args in request.form) or not len(request.form) == 4:
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid arguments'})

    # Check for valid amount
    if float(request.form['amount']) < 0:
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid amount'})

    # Check for valid market
    if not wrapper.is_valid_market(request.form['base-currency'],
                                   request.form['counter-currency']):
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid market'})

    # Check for valid order-type
    if not (request.form['order-type'] == 'buy' or request.form['order-type'] == 'sell'):
        exchangeLock.release()
        return jsonify({'success': False, 'message': 'invalid order-type'})

    # Get rate to send order at
    quantity = float(request.form['amount'])
    formattedTicker = wrapper.format_ticker(request.form['base-currency'],
                                            request.form['counter-currency'])
    orderbookResponse = wrapper.get_orderbook(formattedTicker, request.form['order-type'])
    orderRate = get_rate(orderbookResponse, quantity, request.form['order-type'])

    # Check that availble balance is high enough
    if request.form['order-type'] == 'buy':
        balance = wrapper.get_balance(request.form['counter-currency'])['result']['Balance']
        # Check that balance of counter-currency * rate is greater than quantity needed
        if balance * orderRate < quantity:
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'insufficient balance'})
    else:
        balance = wrapper.get_balance(request.form['base-currency'])['result']['Balance']
        # Check that balance is greater than quantity to sell
        if balance < quantity:
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'insufficient balance'})

    # All checks passed, place order
    if request.form['order-type'] == 'buy':
        apiResponse = wrapper.buy_limit(formattedTicker, quantity, orderRate)
        if apiResponse['success'] == True:
            exchangeLock.release()
            return jsonify({'success': True, 'message': 'order placed'})
        else:
            # Buy request failed
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'failed to place order'})
    else:
        apiResponse = wrapper.sell_limit(formattedTicker, quantity, orderRate)
        if apiResponse['success'] == True:
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'failed to place order'})
        else:
            # Sell request failed
            exchangeLock.release()
            return jsonify({'success': True, 'message': 'order placed'})

if __name__ == '__main__':
    app.run()
