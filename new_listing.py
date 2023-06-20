import multiprocessing
import time
from threading import Thread
import requests
from config import kc_client

from rsrcs.coin_lib import keyboard_sell, profit_tracker, limit_buy_token, market_buy_token, keyboard_buy
from rsrcs.useful_funcs import print_bot_name, awaiting_message

COIN_NAME = 'OLE'
DELAY = 0.001  # delay(in seconds) to get coin price again as soon as listing. 0 means no update

USDT_AMOUNT = 5

OFFSET = 11  # percentage added to OG order price. ie: if price 100 retrieved and offset is 1, order price will be 101


# good numbers for offset: around 5 to 30 percent for world premiers, and 1 to 5 for normal new listings.


def main():
    proc = multiprocessing.Process(target=awaiting_message)
    proc.start()

    while True:  # keep getting coin until it has been listed!
        coin = kc_client.get_fiat_prices(symbol=COIN_NAME)
        # print(coin)
        if coin:  # if coin hasn't been listed yet, go on next iteration
            break

    proc.terminate()
    print(f'\r ')

    cur_price = float(coin[COIN_NAME])
    coin_details = requests.request('GET', 'https://api.kucoin.com' + f'/api/v1/symbols/{COIN_NAME}-USDT').json()[
        'data']

    if DELAY != 0:
        time.sleep(DELAY)
        cur_price = float(kc_client.get_fiat_prices(symbol=COIN_NAME)[COIN_NAME])  # get fiat or use asks

    print(f"cur_price = {cur_price}")
    cur_price += cur_price * (OFFSET / 100)
    # print(f"offset_price = {cur_price}")

    order_id = limit_buy_token(COIN_NAME, coin_details, USDT_AMOUNT, cur_price)

    Thread(target=profit_tracker, args=[COIN_NAME, float(cur_price)]).start()

    keyboard_sell(COIN_NAME, coin_details, order_id, 'USDT')  # page-up -- limit sell, page-down -- market sell

    '''
    Uncomment the following line to enable keyboard buying, this will only be used for cases where limit order hasn't 
    been successfully executed. 
    
    MAKE SURE TO CANCEL CURRENT ORDER WITH 'c', then you will be able to place a new limit order with 'b'
    '''

    # keyboard_buy(COIN_NAME, USDT_AMOUNT, OFFSET, order_id)


if __name__ == '__main__':
    print_bot_name()
    main()
