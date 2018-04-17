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
from flask import jsonify

'''
This class is used to make requests to the Bittrex API. It abstracts away the
url request formatting from the user.

Function calls to this wrapper will come in the following form as a dictionary
{
    'success': BOOLEAN,
    'field1': TYPE,
    'field2': TYPE
}
'''
class Wrapper:
    '''
    Requires a filename which must be the name of a .txt file the first line
    must be the API 'key', and the second line the API 'secret'.
    '''
    def __init__(self, filename):
        privateData = open(filename, "r")
        self.apiKey = privateData.readline().rstrip('\n')
        self.apiSecret = privateData.readline().rstrip('\n')
        self.url = 'https://bittrex.com/api/v1.1/{requestType}/{command}?'

    '''
    This function acts as an abstraction for the api functions, it will take
    in the arguments for the command and created the API request.
    It will handle HMAC signatures, urlencoding, and request headers.
    '''
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

    '''
    Return the bid, ask, and last price for a given market
    Response:
    {
        'success': BOOLEAN,
        'bid': FLOAT,
        'ask': FLOAT,
        'last': FLOAT
    }
    '''
    def get_ticker(self, market):
        apiResponse = self.process_command('getticker', 'public',
                                           {'market': str(market)})

        # If the API call was successful return the corresponding dictionary
        if apiResponse['success'] == True:
            return {'success': True,
                    'bid': float(apiResponse['result']['Bid']),
                    'ask': float(apiResponse['result']['Ask']),
                    'last': float(apiResponse['result']['Last'])}
        else:
            return {'success': False}

    '''
    Return the list of open orders for a given market
    Response:
    {
        'success': BOOLEAN,
        'book': [{
                    'Quantity': FLOAT
                    'Rate': FLOAT
                 }, {
                    'Quantity': FLOAT
                    'Rate': FLOAT
                 }]
    }
    '''
    def get_orderbook(self, market, booktype):
        apiResponse = self.process_command('getorderbook', 'public',
                                           {'market': str(market),
                                            'type': str(booktype)})

        # If the API call was successful return the corresponding dictionary
        if apiResponse['success'] == True:
            return {'success': True,
                    'book': apiResponse['result']}
        else:
            return {'success': False}

    '''
    Return the availble balance for a given currency
    Response:
    {
        'success': BOOLEAN,
        'balance': FLOAT
    }
    '''
    def get_balance(self, currency):
        apiResponse = self.process_command('getbalance', 'account',
                                           {'currency': str(currency)})
        # If the API call was successful return the corresponding dictionary
        if apiResponse['success'] == True:
            return {'success': True,
                    'balance': float(apiResponse['result']['Balance'])}
        else:
            return {'success': False}

    '''
    Place a sell order for a given market with a set price and amount
    Response:
    {
        'success': BOOLEAN,
        'uuid': STRING
    }
    '''
    def sell_limit(self, market, amount, price):
        apiResponse = self.process_command('selllimit', 'market',
                                           {'market': market,
                                            'quantity': amount,
                                            'rate': price})
        # If the API call was successful return the corresponding dictionary
        if apiResponse['success'] == True:
            return {'success': True,
                    'uuid': apiResponse['result']['uuid']}
        else:
            return {'success': False}

    '''
    Place a buy order for a given market with a set price and amount
    Response:
    {
        'success': BOOLEAN,
        'uuid': STRING
    }
    '''
    def buy_limit(self, market, amount, price):
        apiResponse = self.process_command('buylimit', 'market',
                                            {'market': market,
                                             'quantity': amount,
                                             'rate': price})
        # If the API call was successful return the corresponding dictionary
        if apiResponse['success'] == True:
            return {'success': True,
                    'uuid': apiResponse['result']['uuid']}
        else:
            return {'success': False}

    '''
    Cancel an order with the specific uuid
    {
        'success': BOOLEAN
    }
    '''
    def cancel_order(self, uuid):
        apiResponse = self.process_command('cancel', 'market',
                                           {'uuid': uuid})
        # If the API call was successful return the corresponding dictionary
        if apiResponse['success'] == True:
            return {'success': True}
        else:
            return {'success': False}

    '''
    Return the details of a specfic order
    {
        'success': BOOLEAN,
        'uuid': STRING,
        'market': STRING,
        'quantity': FLOAT,
        'price': FLOAT,
        'commissionPaid': FLOAT,
        'isOpen': BOOLEAN
    }
    '''
    def get_order(self, uuid):
        apiResponse = self.process_command('getorder', 'account',
                                           {'uuid': uuid})

        # If the API call was successful return the corresponding dictionary
        if apiResponse['success'] == True:
            return {'success': True,
                    'uuid': apiResponse['result']['OrderUuid'],
                    'market': apiResponse['result']['Exchange'],
                    'quantity': float(apiResponse['result']['Quantity']),
                    'price': float(apiResponse['result']['Price']),
                    'commissionPaid': float(apiResponse['result']['CommissionPaid']),
                    'isOpen': apiResponse['result']['isOpen']}
        else:
            return {'success': False}

    # Return True/False based on API response
    def is_valid_currency(self, currency):
        response = self.process_command('getcurrencies', 'public')
        for i in response['result']:
            if (i['Currency'] == currency):
                return True
        return False

    # Return True/False based on API response
    def is_valid_market(self, currency0, currency1):
        market = str(currency1 + '-' + currency0)
        response = self.process_command('getmarketsummary', 'public',
                                        {'market': market})
        if response['success'] == 1:
            return True
        else:
            return False
