from decimal import Decimal

import requests
from kucoin_config import kc_client

from rsrcs.coin_lib import keyboard_sell, profit_tracker, limit_buy_token, market_buy_token, keyboard_buy

symbol = 'OMN'

# USDT_AMOUNT = 0
USDT_AMOUNT = 1

OFFSET = 9  # percentage added to OG order price. ie: if price 100 retrieved and offset is 1, order price will be 101


offsetDecimal = Decimal(OFFSET) / Decimal(100)
# good numbers for offset: around 5 to 30 percent for world premiers, and 1 to 5 for normal new listings.

def main():
    coin_details = None
    # coin_details = {'symbol': 'CANDY-USDT', 'name': 'CANDY-USDT', 'baseCurrency': 'CANDY', 'quoteCurrency': 'USDT', 'feeCurrency': 'USDT', 'market': 'USDS', 'baseMinSize': '1', 'quoteMinSize': '0.1', 'baseMaxSize': '10000000000', 'quoteMaxSize': '99999999', 'baseIncrement': '0.0001', 'quoteIncrement': '0.0001', 'priceIncrement': '0.0001', 'priceLimitRate': '0.1', 'minFunds': '0.1', 'isMarginEnabled': False, 'enableTrading': False}
    # coin_details = {'symbol': 'PIP-USDT', 'name': 'PIP-USDT', 'baseCurrency': 'PIP', 'quoteCurrency': 'USDT', 'feeCurrency': 'USDT', 'market': 'USDS', 'baseMinSize': '1', 'quoteMinSize': '0.1', 'baseMaxSize': '10000000000', 'quoteMaxSize': '99999999', 'baseIncrement': '0.0001', 'quoteIncrement': '0.0001', 'priceIncrement': '0.0001', 'priceLimitRate': '0.1', 'minFunds': '0.1', 'isMarginEnabled': False, 'enableTrading': False}
    coin_details = {'symbol': 'OMN-USDT', 'name': 'OMN-USDT', 'baseCurrency': 'OMN', 'quoteCurrency': 'USDT', 'feeCurrency': 'USDT', 'market': 'USDS', 'baseMinSize': '10', 'quoteMinSize': '0.1', 'baseMaxSize': '10000000000', 'quoteMaxSize': '99999999', 'baseIncrement': '0.0001', 'quoteIncrement': '0.00001', 'priceIncrement': '0.00001', 'priceLimitRate': '0.1', 'minFunds': '0.1', 'isMarginEnabled': False, 'enableTrading': False}
    while True and not coin_details:
        coin_details = requests.request('GET', 'https://api.kucoin.com' + f'/api/v1/symbols/{symbol}-USDT').json()[
            'data']
        if coin_details:
            break

    while True:  # keep getting coin until it has been listed!
        coin = kc_client.get_fiat_prices(symbol=symbol)
        print(coin)
        if coin:  # if coin hasn't been listed yet, go on next iteration
            break
        # time.sleep(random.randint(1, 2))

    cur_price = str(coin[symbol])
    print(f"cur_price = {cur_price}")

    cur_price = Decimal(cur_price)
    cur_price += cur_price * offsetDecimal

    cur_price = float(cur_price)

    order_id = limit_buy_token(symbol, coin_details, USDT_AMOUNT, cur_price)
    print(f"order id = {order_id}")
    return True

if __name__ == '__main__':
    # print_bot_name()
    while True:
        try:
            val = main()
            if val:
                break
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            print(e.__str__())
