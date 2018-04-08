# This file will be used to test the Bittrex API wrapperself.
# Created by Izak Fritz 04-07-18
# For the Stably team

import bittrexWrapper

# Test get_ticker by checking that 'success' field is true for valid markets
def test_get_ticker(wrapperInstance):
    print ("Testing 'get_ticker'...")

    output0 = wrapperInstance.get_ticker("USDT-BTC")
    assert (output['success'] == 1), "get_ticker failed: API call failed"

    output1 = wrapperInstance.get_ticker("USDT-ETH")
    assert (output['success'] == 1), "get_ticker failed: API call failed"

    output2 = wrapperInstance.get_ticker("VOID")
    assert (output['success'] == 0), "get_ticker failed: Success on fake market"

    print ("'get_ticker' passed all tests\n")

# Test get_orderbook by checking all booktypes on valid markets
def test_get_orderbook(wrapperInstance):
    print ("Testing 'get_orderbook'...")

    output0 = wrapperInstance.get_orderbook("USDT-ETH", "sell")
    assert (output['success'] == 1), "get_orderbook 'sell' failed: valid API call failed"

    output1 = wrapperInstance.get_orderbook("USDT-ETH", "buy")
    assert (output['success'] == 1), "get_orderbook 'buy' failed: valid API call failed"

    output2 = wrapperInstance.get_orderbook("USDT-ETH", "sell")
    assert (output['success'] == 1), "get_orderbook 'both' failed: valid API call failed"

    output3 = wrapperInstance.get_orderbook("USDT-ETH", "NONE")
    assert (output['success'] == 0), "get_orderbook 'VOID' failed: Success on fake booktype"

    output4 = wrapperInstance.get_orderbook("VOID", "both")
    assert (output['success'] == 0), "get_orderbook failed: Success on fake market"

    print ("'get_ticker' passed all tests\n")

# Test get_balance by checking that success is true
def test_get_balance(wrapperInstance):
    print ("Testing 'get_balance...'")

    output0 = wrapperInstance.get_balance("ETH")
    assert (output['success'] == 1), "get_balance failed: API call failed on valid currency"

    output1 = wrapperInstance.get_balance("VOID")
    assert (output['success'] == 0), "get_balance failed: Success on fake currency"

    print ("'get_balance' passed all tests\n")


# Main function will call all of the tests
def main():
    print ("Running Bittrex wrapper tests...\n")
    wrapperInstance = bittrexWrapper.Wrapper("keys.txt")

    test_get_ticker(wrapperInstance)
    test_get_orderbook(wrapperInstance)

if __name__=="__main__":
    main()
