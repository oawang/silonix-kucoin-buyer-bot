from decimal import Decimal
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
import concurrent
import time
import datetime
import requests
from kucoin_config import kc_client

from rsrcs.coin_lib import keyboard_sell, profit_tracker, limit_buy_token, market_buy_token, keyboard_buy

# symbol = 'OMN'
symbol = 'VCORE'

# USDT_AMOUNT = 0
USDT_AMOUNT = 20

# OFFSET = 9  # percentage added to OG order price. ie: if price 100 retrieved and offset is 1, order price will be 101
# good numbers for offset: around 5 to 30 percent for world premiers, and 1 to 5 for normal new listings.


# 是否使用线程批量提交多个挂单0.09,0.19,0.29,0.39,0.49
use_thread_pool = True

# OFFSET = 9
# percentage added to OG order price. ie: if price 100 retrieved and offset is 1, order price will be 101
# good numbers for offset: around 5 to 30 percent for world premiers, and 1 to 5 for normal new listings.

offsetDecimal_9 = Decimal(9) / Decimal(100)
offsetDecimal_19 = Decimal(19) / Decimal(100)
offsetDecimal_29 = Decimal(29) / Decimal(100)
offsetDecimal_39 = Decimal(39) / Decimal(100)
offsetDecimal_49 = Decimal(49) / Decimal(100)

offsetDecimalArr = [
    offsetDecimal_9,
    offsetDecimal_19,
    offsetDecimal_29,
    # offsetDecimal_39,
    # offsetDecimal_49
]


def check_time_string(time_string):
    format_string = '%H:%M:%S'
    try:
        return datetime.datetime.strptime(time_string, format_string)
    except ValueError:
        # print('时间格式不正确')
        pass

def main(schedulerTime, timedExecFlag = True):

    if timedExecFlag and not schedulerTime:
        print("定时执行时间不能为空, HH:MM:SS")
        return

    current_time = time.strftime('%H:%M:%S')
    if schedulerTime:
        if not check_time_string(schedulerTime):
            print("定时执行时间格式不正确, HH:MM:SS")
            return
        print(f"现在时间是 {current_time}，指定执行时间是 {schedulerTime}！")

    if timedExecFlag:
        while current_time <= schedulerTime:
            current_time = time.strftime('%H:%M:%S')
            time.sleep(0.5)
    # 执行任务
    print(f"现在时间是 {current_time}，可以开始执行任务了！")

    usdt_amount = USDT_AMOUNT
    coin_details = None
    # coin_details = {'symbol': 'VCORE-USDT', 'name': 'VCORE-USDT', 'baseCurrency': 'VCORE', 'quoteCurrency': 'USDT', 'feeCurrency': 'USDT', 'market': 'USDS', 'baseMinSize': '100', 'quoteMinSize': '0.1', 'baseMaxSize': '10000000000', 'quoteMaxSize': '99999999', 'baseIncrement': '0.0001', 'quoteIncrement': '0.000001', 'priceIncrement': '0.000001', 'priceLimitRate': '0.1', 'minFunds': '0.1', 'isMarginEnabled': False, 'enableTrading': False}
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

    # usdt_amount = 1
    if use_thread_pool:
        batch_create_order_use_pool(symbol, coin_details, usdt_amount, cur_price, offsetDecimalArr)
    else:
        order_val = do_create_order(symbol, coin_details, usdt_amount, cur_price, offsetDecimal_9)
        # order id = 649178a6de838200012ae994
        print(f"order id = {order_val}")
    return True


def do_create_order(symbol, coin_details, usdt_amount: int, cur_price: Decimal, offsetDecimal: Decimal):
    cur_price += cur_price * offsetDecimal
    cur_price = float(cur_price)
    order_val = None
    try:
        order_val = limit_buy_token(symbol, coin_details, usdt_amount, cur_price)
        # order id = 649178a6de838200012ae994
        print(f"order id = {order_val}")
    except Exception as e:
        print(e.__str__())
    return order_val

def batch_create_order_use_pool(symbol, coin_details, usdt_amount: int, cur_price: Decimal, offsetDecimalArr: [], timeout = 5):
    start = datetime.datetime.now()
    size = len(offsetDecimalArr)
    executor_size = size
    futures = []
    with ProcessPoolExecutor(executor_size) as executor:
        for offsetDecimal in offsetDecimalArr:
            futures.append(executor.submit(do_create_order, symbol, coin_details, usdt_amount, cur_price, offsetDecimal))
        try:
            for future in as_completed(futures, timeout=timeout):
                future.result(timeout=timeout)
        except concurrent.futures._base.TimeoutError:
            print("主线程：达到了程序的最大超时时间，程序退出")
            stop_process_pool(executor)
    print('执行完成', datetime.datetime.now() - start)


def stop_process_pool(executor):
    for pid, process in executor._processes.items():
        process.terminate()
    # executor.shutdown()


if __name__ == '__main__':
    # print_bot_name()
    try:
        schedulerTime = '17:59:56'
        main(schedulerTime)
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        print(e.__str__())

