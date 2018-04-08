# This file will be used to test the Bittrex API wrapperself.
# Created by Izak Fritz 04-07-18
# For the Stably team

import BittrexWrapper

# Test get_ticker by checking that 'success' field is true for valid markets
def test_get_ticker(WrapperInstance):
    print ("Testing 'get_ticker'...")

    output0 = WrapperInstance.get_ticker("USDT-BTC")
    assert (output['success'] == 1), "get_ticker failed: API call failed"

    output1 = WrapperInstance.get_ticker("USDT-ETH")
    assert (output['success'] == 1), "get_ticker failed: API call failed"

    output2 = WrapperInstance.get_ticker("VOID")
    assert (output['success'] == 0), "get_ticker failed: Success on fake market"

    print ("'get_ticker' passed all tests\n")

# Test get_orderbook by checking all booktypes on valid markets
def test_get_orderbook(WrapperInstance):
    print ("Testing 'get_orderbook'...)

    output0 = WrapperInstance.get_orderbook("USDT-ETH", "sell")
    assert (output['success'] == 1), "get_orderbook 'sell' failed: API call failed"

    output1 = WrapperInstance.get_orderbook("USDT-ETH", "buy")
    assert (output['success'] == 1), "get_orderbook 'buy' failed: API call failed"

    output2 = WrapperInstance.get_orderbook("USDT-ETH", "sell")
    assert (output['success'] == 1), "get_orderbook 'both' failed: API call failed"

    output3 = WrapperInstance.get_orderbook("USDT-ETH", "NONE")
    assert (output['success'] == 0), "get_orderbook 'VOID' failed: Success on fake booktype"

    output4 = WrapperInstance.get_orderbook("VOID", "both")
    assert (output['success'] == 0), "get_orderbook failed: Success on fake market"

    print ("'get_ticker' passed all tests\n")

# Main function will call all of the tests
def main():
    print ("Running Bittrex wrapper tests...\n")
