import hashlib
import time
import json
import websockets
import asyncio

# Ваши API ключи и passphrase
api_key = "bg_660c4bcf9e0a9483ce711e0dbbf4c595"
api_secret = "6bc9b6713cb3c34f93b88aeac43998d665979ea2c301c4b5e51821b7a79ce511"
passphrase = "QWERTYasdfg808801"


# Генерация подписи для авторизации
def generate_signature(api_key, api_secret, passphrase):
    timestamp = str(int(time.time() * 1000))  # Генерация метки времени
    msg = timestamp + "GET" + "/api/v1/spot/account"
    signature = hashlib.sha256((api_secret + msg).encode('utf-8')).hexdigest()  # Подпись
    return timestamp, signature


async def connect():
    uri = "wss://ws.bitget.com/mix/v1/stream"  # URL для WebSocket фьючерсов (USDT маржа)
    async with websockets.connect(uri) as websocket:
        # Генерация подписи
        timestamp, signature = generate_signature(api_key, api_secret, passphrase)

        # Сообщение для авторизации
        login_message = {
            "op": "login",
            "args": [{
                "apiKey": api_key,
                "passphrase": passphrase,
                "timestamp": timestamp,
                "sign": signature
            }]
        }
        await websocket.send(json.dumps(login_message))  # Отправляем сообщение авторизации

        # Подписка на канал (например, свечи 1 минута для BTC/USDT)
        subscribe_message = {
            "op": "subscribe",
            "args": [{
                "channel": "candle1m",  # Канал свечей с таймфреймом 1 минута
                "instId": "BTCUSDT_UMCBL"  # Пара для фьючерсов
            }]
        }
        await websocket.send(json.dumps(subscribe_message))  # Подписка на канал

        # Получение данных
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(data)


# Запуск подключения
asyncio.run(connect())









