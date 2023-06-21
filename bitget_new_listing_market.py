from concurrent.futures import ProcessPoolExecutor, as_completed, wait
import concurrent
import datetime
from decimal import Decimal
from bitget_config import marketApi, orderApi, accountApi, publicApi

symbol = 'alpha1usdt_spbl'
# symbol = 'pepeusdt_spbl'
# symbol = 'sclpusdt_spbl'

# USDT_AMOUNT = 0
USDT_AMOUNT = 40

# 是否提交订单
submitOrder = False

# 是否使用线程批量提交多个挂单0.09,0.19,0.29,0.39,0.49
use_thread_pool = True

# OFFSET = 9
# percentage added to OG order price. ie: if price 100 retrieved and offset is 1, order price will be 101
# good numbers for offset: around 5 to 30 percent for world premiers, and 1 to 5 for normal new listings.

useOffset9 = False

if useOffset9:
    offsetDecimal_9 = Decimal(9) / Decimal(100)
    offsetDecimal_19 = Decimal(19) / Decimal(100)
    offsetDecimal_29 = Decimal(29) / Decimal(100)
    offsetDecimal_39 = Decimal(39) / Decimal(100)
    offsetDecimal_49 = Decimal(49) / Decimal(100)
    offsetDecimal_59 = Decimal(5) / Decimal(100)
else:
    offsetDecimal_9 = Decimal(5) / Decimal(100)
    offsetDecimal_19 = Decimal(10) / Decimal(100)
    offsetDecimal_29 = Decimal(15) / Decimal(100)
    offsetDecimal_39 = Decimal(20) / Decimal(100)
    offsetDecimal_49 = Decimal(25) / Decimal(100)
    offsetDecimal_59 = Decimal(30) / Decimal(100)

offsetDecimalArr = [
    offsetDecimal_9,
    offsetDecimal_19,
    offsetDecimal_29,
    offsetDecimal_39,
    offsetDecimal_49,
    offsetDecimal_59
]

def main():
    coin_details = None
    usdt_amount = USDT_AMOUNT
    # coin_details = {'symbol': 'PEPEUSDT_SPBL', 'symbolName': 'PEPEUSDT', 'baseCoin': 'PEPE', 'quoteCoin': 'USDT', 'minTradeAmount': '1', 'maxTradeAmount': '0', 'takerFeeRate': '0.001', 'makerFeeRate': '0.001', 'priceScale': '11', 'quantityScale': '0', 'quotePrecision': '11', 'status': 'online', 'minTradeUSDT': '5', 'buyLimitPriceRatio': '0.1', 'sellLimitPriceRatio': '0.1'}
    while True and not coin_details:
        info = publicApi.product(symbol)
        coin_details = info['data']
        if coin_details:
            # 最小交易的USDT数量
            if 'minTradeUSDT' in coin_details and coin_details['minTradeUSDT']:
                minTradeUSDT = int(coin_details['minTradeUSDT'])
                if usdt_amount < minTradeUSDT:
                    usdt_amount = minTradeUSDT + 1
            break

    while True:  # keep getting coin until it has been listed!
        info = marketApi.ticker(symbol)
        ticker = info['data']
        # print(ticker)
        if ticker and 'close' in ticker:  # if coin hasn't been listed yet, go on next iteration
            if float(ticker['close']) != 0:
                break
            else:
                print('cur price is 0.')
        # time.sleep(random.randint(1, 2))

    cur_price = str(ticker['close'])
    print(f"cur_price = {cur_price}")

    cur_price = Decimal(cur_price)
    priceScale = int(coin_details['priceScale'])
    quantityScale = int(coin_details['quantityScale'])

    # usdt_amount = 1
    if submitOrder:
        if use_thread_pool:
            batch_create_order_use_pool(usdt_amount, cur_price, offsetDecimalArr, priceScale, quantityScale)
        else:
            do_create_order(usdt_amount, cur_price, offsetDecimal_9, priceScale, quantityScale)
    else:
        print("不提交订单")


def do_create_order(usdt_amount, cur_price: Decimal, offsetDecimal: Decimal, priceScale: int, quantityScale: int):
    cur_price += cur_price * offsetDecimal
    cur_price = float(round(cur_price, priceScale))
    buy_amount = int(round(usdt_amount / cur_price, quantityScale))
    order_val = None
    try:
        order_val = orderApi.orders(symbol, buy_amount, 'buy', 'limit', 'normal', cur_price)
        print(f"limit buy order {order_val} placed!")
    except Exception as e:
        print(e.__str__())
    return order_val

def batch_create_order_use_pool(usdt_amount, cur_price: Decimal, offsetDecimalArr: [], priceScale: int, quantityScale: int, timeout = 5):
    start = datetime.datetime.now()
    size = len(offsetDecimalArr)
    executor_size = size
    futures = []
    with ProcessPoolExecutor(executor_size) as executor:
        for offsetDecimal in offsetDecimalArr:
            futures.append(executor.submit(do_create_order, usdt_amount, cur_price, offsetDecimal, priceScale, quantityScale))
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
    try:
        main()
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        print(e.__str__())

