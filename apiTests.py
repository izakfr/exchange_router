# This file will be used to test the API POST and GET requests.
# Created by Izak Fritz 04-09-18
# For the Stably team

import json
import requests

# Define the top level URL below
apiURL = "http://localhost:5000/api/v1.0/"

# Test get_fill_price
# The API call get_fill_price should return a JSON object with the structure
# {
#   'success': BOOLEAN,
#   'avg_price': FLOAT
# }
def get_fill_price_test():
    print ("Testing get fill price...")

    # Define the baseURL for all the GET requests
    baseURL = apiURL + "get-fill-price?base-currency={0}&counter-currency={1}&quantity={2}"

    # All these API calls should be successful
    testURL0 = baseURL.format("ETH", "USDT", 1)
    response0 = requests.get(testURL0).json()
    assert (response0['success'] == 1), "get-fill-price failed: API call failed"

    testURL1 = baseURL.format("ETH", "USDT", 100)
    response1 = requests.get(testURL1).json()
    assert (response1['success'] == 1), "get-fill-price failed: API call failed"

    testURL2 = baseURL.format("BTC", "USDT", 1)
    response2 = requests.get(testURL2).json()
    assert (response2['success'] == 1), "get-fill-price failed: API call failed"

    testURL3 = baseURL.format("BTC", "USDT", 100)
    response3 = requests.get(testURL3).json()
    assert (response3['success'] == 1), "get-fill-price failed: API call failed"

    # All these API calls should not be successful
    testURL4 = baseURL.format("VOID", "USDT", 1)
    response4 = requests.get(testURL4).json()
    assert (response4['success'] == 0), "get-fill-price failed: success on fake market"

    testURL5 = baseURL.format("ETH", "VOID", 1)
    response5 = requests.get(testURL5).json()
    assert (response5['success'] == 0), "get-fill-price failed: success on fake market"

    testURL6 = baseURL.format("ETH", "USDT", -1)
    response6 = requests.get(testURL6).json()
    assert (response6['success'] == 0), "get-fill-price failed: success on negative quantity"

    print ("get fill price passed all tests!\n")

# Test get_currency_balance
# The API call get_currency_balance should return a JSON object with the structure:
# {
#   'success': BOOLEAN,
#   'balance': FLOAT
# }
def get_currency_balance_test():
    print ("Testing get currency balance...")

    # Define the baseURL for all the GET requests
    baseURL = apiURL + "get-currency-balance?currency={0}"

    # All these API calls should be successful
    testURL0 = baseURL.format("ETH")
    response0 = requests.get(testURL0).json()
    assert (response0['success'] == 1), "get-currency-balance failed: API call failed"

    testURL1 = baseURL.format("USDT")
    response1 = requests.get(testURL1).json()
    assert (response1['success'] == 1), "get-currency-balance failed: API call failed"

    testURL2 = baseURL.format("BTC")
    response2 = requests.get(testURL2).json()
    assert (response2['success'] == 1), "get-currency-balance failed: API call failed"

    # All these API calls should not be successful
    testURL3 = baseURL.format("VOID")
    response3 = requests.get(testURL3).json()
    assert (response3['success'] == 0), "get-currency-balance failed: success on fake currency"

    print ("get currency balance passed all tests!\n")

# Test send_order
# The API call send_order should return a JSON object with the structure:
# {
#   'result': BOOLEAN
# }
def send_order_test():
    print ("Testing send order...")

    # Define the baseURL for all the GET requests
    baseURL = apiURL + "send-order"

    # All these API calls should be successful
    data0 = {"base-currency": "ETH", "counter-currency": "USDT",
             "order-type": "buy", "amount": .01}
    response0 = requests.post(baseURL, data0).json()
    assert (response0['success'] == 1), "send-order failed: API call failed"

    data1 = {"base-currency": "BTC", "counter-currency": "USDT",
             "order-type": "buy", "amount": .0005}
    response1 = requests.post(baseURL, data1).json()
    assert (response1['success'] == 1), "send-order failed: API call failed"

    # All these API calls should not be successful
    data3 = {"base-currency": "ETH", "counter-currency": "USDT",
             "order-type": "buy", "amount": -1}
    response3 = requests.post(baseURL, data3).json()
    assert (response3['success'] == 0), "send-order failed: API call success on negative quantity"

    print ("send order passed all tests!\n")

# Main function will call all of the tests
def main():
    print ("Testing api calls...")

    # Run all tests
    get_fill_price_test()
    get_currency_balance_test()
    send_order_test()

    print ("All api calls passed!\n")

if __name__=="__main__":
    main()
