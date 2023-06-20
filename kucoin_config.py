from kucoin.client import Client
# from telethon import TelegramClient

# Telegram Information!
api_id = 'Your Telegram API ID'
api_hash = 'Your Telegram API hash'

# Telegram client creation 
# tel_client = TelegramClient('anon', api_id, api_hash)

# KuCoin Information!
api_key = '6487f01af76ac4000178c0b5'
api_secret = '1307e7e8-0c8c-48e8-8ab5-8f4c7f0bbbb6'
api_passphrase = 'iYiY73vd#jWpWZG'

# KuCoin Client creation 
kc_client = Client(api_key, api_secret, api_passphrase)

# DISCORD HEADERS FOR SCRAPING
discord_headers = {
    'authorization': 'Your Discord authorization key'
}