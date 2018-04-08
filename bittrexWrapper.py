# This file will be used to create instances of a Bittrex wrapper
# Created by Izak Fritz 04-07-18
# For the Stably team

import urllib.request
from urllib.parse import urlencode
import hmac
import hashlib
import json
import requests
import time

# This class is used to make requests to the Bittrex API. It abstracts away the
# url request formatting from the user.

class Wrapper:
    # Requires a filename which must be the name of a .txt file the first line
    # must be the API "key", and the second line the API "secret".
    def __init__(self, filename):
        privateData = open(filename, "r")
        self.apiKey = privateData.readline().rstrip('\n')
        self.apiSecret = privateData.readline().rstrip('\n')
        self.url = 'https://bittrex.com/api/v1.1/{req_type}/{cmnd}?'

    # This function acts as an abstraction for the api functions, it will take
    # in the arguments for the command and created the API request
    # It will handle HMAC signatures, urlencoding, and request headers
    def proccess_command(self, cmnd, requestType, requestArgs={}):
        # TODO
        assert(0)
        return -1

    # Return the JSON response with 'Bid', 'Ask', and 'Last' for a given market
    def get_ticker(self, market):
        # TODO
        assert(0)
        return -1

    # Return the JSON response with a list of open orders for a given market
    def get_orderbook(self, market):
        # TODO
        assert(0)
        return -1

    # Return the JSON response with the availble balance for a given currency
    def get_balance(self, currency):
        # TODO
        assert(0)
        return -1

    # Return the JSON response for placing a sell order for a given market with
    # a set price and amount
    def sell_limit(self, baseCurrency, counterCurrency, amount, price):
        # TODO
        assert(0)
        return -1

    # Return the JSON response for placing a buy order for a given market with
    # a set price and amount
    def buy_limit(self, baseCurrency, counterCurrency, amount, price):
        # TODO
        assert(0)
        return -1

    # Return the JSON response for cancelling an order with the specific uuid
    def cancel_order(self, uuid):
        # TODO
        assert(0)
        return -1

    # Return the JSON response for getting the details of a specfic order
    def get_order(self, orderID):
        # TODO
        assert(0)
        return -1
