import asyncio
from config import api_key, secret_key
from setting import symbol, kline_time, rsi_len
from pybit.unified_trading import HTTP

session = HTTP(testnet = False, demo = True, api_key=api_key, api_secret=secret_key)

async def run():
    while True:
        close_price = []

        response = session.get_kline(
            category='linear',
            symbol = symbol, 
            interval = kline_time,
            limit = 3,
        )
        klines = response.get('result', {}).get('list', [])
        klines = sorted(klines,key=lambda x: int(x[0]))
        
        for candle in klines:
            close_price_for_list = float(candle[4])
            close_price.append(close_price_for_list)
        print(close_price[-4:])

        await asyncio.sleep(60)

if __name__ == '__main__':
     asyncio.run(run())

