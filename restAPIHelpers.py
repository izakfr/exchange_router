# This file contains helper functions for the restAPI to use
# Created by Izak Fritz 04-15-18
# For the Stably team

# Define functions below:

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
