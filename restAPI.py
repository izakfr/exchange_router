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
import restAPIHelpers as helpers

app = Flask(__name__)

# Thread lock for concurrent requests
exchangeLock = threading.Lock()

# Order queue to continously check for filled orders
orderQueue = Queue()

# Declare an instance of a Bittrex wrapper
wrapper = bittrexWrapper.Wrapper("keys.txt")

# Continously checks for new orders
@app.before_first_request
def api_init():
    def check_orders():
        while True:
            # TODO: acquire lock and check orders
            exchangeLock.acquire()

            # If queue is not empty get all orders and check on them
            size = orderQueue.qsize()
            for i in range(0, size):
                orderUUID = orderQueue.get()
                orderResponse = wrapper.get_order(orderUUID)
                # If order is filled, print it out to a file
                if orderResponse['isOpen'] == False:
                    fiatTransacted = float('%.2f'%(orderResponse['price'] + orderResponse['commissionPaid']))
                    helpers.output_to_file("orders.txt",
                                           orderResponse['type'],
                                           fiatTransacted,
                                           orderResponse['timestamp'],
                                           "Bittrex")
                else:
                    # Put the order back on the queue
                    orderQueue.put(orderUUID)

            exchangeLock.release()
            time.sleep(10)

    orderThread = threading.Thread(target=check_orders)
    orderThread.start()

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

    avgPrice = helpers.get_average_fill_price(orderbookResponse, quantityToFill)

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
    balance = wrapper.get_balance(request.args['currency'])['balance']

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
    orderRate = helpers.get_rate(orderbookResponse, quantity, request.form['order-type'])

    # Check that availble balance is high enough
    if request.form['order-type'] == 'buy':
        balance = wrapper.get_balance(request.form['counter-currency'])['balance']
        # Check that balance of counter-currency * rate is greater than quantity needed
        if balance * orderRate < quantity:
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'insufficient balance'})
    else:
        balance = wrapper.get_balance(request.form['base-currency'])['balance']
        # Check that balance is greater than quantity to sell
        if balance < quantity:
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'insufficient balance'})

    # All checks passed, place order
    if request.form['order-type'] == 'buy':
        apiResponse = wrapper.buy_limit(formattedTicker, quantity, orderRate)
        # If order was successful add order to orderQueue and return
        if apiResponse['success'] == True:
            orderQueue.put(apiResponse['uuid'])
            exchangeLock.release()
            return jsonify({'success': True, 'message': 'order placed'})
        else:
            # Buy request failed
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'failed to place order'})
    else:
        apiResponse = wrapper.sell_limit(formattedTicker, quantity, orderRate)
        # If order was successful add order to orderQueue and return
        if apiResponse['success'] == True:
            # Add order uuid to the orderQueue
            orderQueue.put(apiResponse['uuid'])
            exchangeLock.release()
            return jsonify({'success': False, 'message': 'failed to place order'})
        else:
            # Sell request failed
            exchangeLock.release()
            return jsonify({'success': True, 'message': 'order placed'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
