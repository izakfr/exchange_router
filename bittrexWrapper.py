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
        self.url = 'https://bittrex.com/api/v1.1/{requestType}/{command}?'

    # This function acts as an abstraction for the api functions, it will take
    # in the arguments for the command and created the API request
    # It will handle HMAC signatures, urlencoding, and request headers
    def process_command(self, command, requestType, requestArgs={}):
        # Create a nonce by using the current time
        nonce = str(int(time.time() * 10))
        requestURL = self.url.format(requestType=requestType, command=command)

        # Public requests do not require api keys to be encoded in the url
        if requestType != 'public':
            requestURL = "{0}apikey={1}&nonce={2}&".format(
                requestURL, self.apiKey, nonce)

        # Encode the arguments into the url
        requestURL += urlencode(requestArgs)

        # Sign the API request with secret key using HMAC
        apiSignature = hmac.new(self.apiSecret.encode(),
                           requestURL.encode(),
                           hashlib.sha512).hexdigest()

        # Send the request and return the JSON
        return requests.get(requestURL, headers={"apisign": apiSignature}).json()

    # Format market ticker
    def format_ticker(self, baseCurrency, counterCurrency):
        return str(counterCurrency) + "-" + str(baseCurrency)

    # Return the JSON response with 'Bid', 'Ask', and 'Last' for a given market
    def get_ticker(self, market):
        return self.process_command("getticker", "public",
                                     {'market': str(market)})

    # Return the JSON response with a list of open orders for a given market
    def get_orderbook(self, market, booktype):
        return self.process_command("getorderbook", "public",
                                     {'market': str(market),
                                      'type': str(booktype)})

    # Return the JSON response with the availble balance for a given currency
    def get_balance(self, currency):
         return self.process_command("getbalance", "account",
                                    {'currency': str(currency)})

    # Return the JSON response for placing a sell order for a given market with
    # a set price and amount
    def sell_limit(self, market, amount, price):
        return self.process_command("selllimit", "market",
                                    {'market': market,
                                     'quantity': amount,
                                     'rate': price})

    # Return the JSON response for placing a buy order for a given market with
    # a set price and amount
    def buy_limit(self, market, amount, price):
        return self.process_command("buylimit", "market",
                                    {'market': market,
                                     'quantity': amount,
                                     'rate': price})

    # Return the JSON response for cancelling an order with the specific uuid
    def cancel_order(self, uuid):
        return self.process_command("cancel", "market",
                                    {'uuid': uuid})

    # Return the JSON response for getting the details of a specfic order
    def get_order(self, uuid):
        return self.process_command("getorder", "account",
                                    {'uuid': uuid})

    # Return True/False based on API response
    def is_valid_currency(self, currency):
        response = self.process_command("getcurrencies", "public")
        for i in response['result']:
            if (i['Currency'] == currency):
                return True
        return False

    # Return True/False based on API response
    def is_valid_market(self, currency0, currency1):
        market = str(currency1 + "-" + currency0)
        response = self.process_command("getmarketsummary", "public",
                                        {'market': market})
        if response['success'] == 1:
            return True
        else:
            return False
