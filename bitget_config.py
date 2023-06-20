import bitget.spot.market_api as market
import bitget.spot.account_api as accounts
import bitget.spot.order_api as order
import bitget.spot.public_api as public

api_key = "bg_4e3966f778815d9e34231cef56980e0c"
secret_key = "af96ada8e0c369f762abef1d9afa0674d122bcec1eebc34c18705eaeaf1b92b7"
passphrase = "8ab58f4c7f0bbbb6"

marketApi = market.MarketApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
accountApi = accounts.AccountApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
publicApi = public.PublicApi(api_key, secret_key, passphrase, use_server_time=False, first=False)