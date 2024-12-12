import asyncio
import json
import websockets
import time
import base64
import hmac
import hashlib

PING_MESSAGE = 'ping'
PONG_MESSAGE = 'pong'

# Replace these with your Bitget API key and secret
apiKey = 'bg_047b6659de65d5bbde4fe51ea0634114'
passphrase = 'qwerty808801'
secretKey = '7268916a299b69342d6d1f06752303abd15289a78a33096a350294fbf878b26d'


def send_ping(websocket):
    asyncio.get_event_loop().create_task(websocket.send(PING_MESSAGE))
    print('send ping')


async def connect():
    uri = "wss://ws.bitget.com/v2/ws/private"
    try:
        async with websockets.connect(uri) as websocket:
            timestamp = str(int(time.time()))
            content = timestamp + 'GET' + '/user/verify'
            hash = hmac.new(bytes(secretKey, 'utf-8'), bytes(content, 'utf-8'), hashlib.sha256).digest()
            signature = base64.b64encode(hash).decode('utf-8')
            auth_request = {
                "op": "login",
                "args": [
                    {
                        "apiKey": apiKey,
                        "passphrase": passphrase,
                        "timestamp": timestamp,
                        "sign": signature
                    }
                ]
            }
            await websocket.send(json.dumps(auth_request))
            auth_response = json.loads(await websocket.recv())
            print(auth_response)

            if auth_response["code"] != 0:
                print(f"Ошибка аутентификации: {auth_response['code']}")
                return

            # Subscribe to the orders channel
            #orders_request = {
              #  "op": "subscribe",
              #  "args": [{
              #      "channel": "orders",
              #      "instType": "UMCBL",
               #     "instId": "default"
               # }]
          #  }
          #  await websocket.send(json.dumps(orders_request))
         #   order_response = json.loads(await websocket.recv())
         #   print(order_response)

             #Подписка на демо трейдинг
            demo_trading = {
                "op": "subscribe",
                "args": [{
                    "instType": "SUSDT-FUTURES",
                    "channel": "ticker",
                    "instId": "SBTCSUSDT"
                }]
            }

            await websocket.send(json.dumps(demo_trading))
            demo_trading_response = json.loads(await websocket.recv())
            print(demo_trading_response)

            if demo_trading_response.get("code") != 0:
                print(f"Подписка не прошла: {demo_trading_response}")
                return
            else:
                print("Подписка на демо трейдинг успешна")

            while True:
                try:
                    message = await websocket.recv()
                    print(f"Received data: {message}")  # Логика обработки данных от WebSocket
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    break



            # Set up ping interval
            timer = asyncio.get_event_loop().call_later(30, send_ping, websocket)

            while True:
                try:
                    message = await websocket.recv()
                except websockets.exceptions.ConnectionClosed:
                    print("Connection lost, attempting to reconnect...")
                    await reconnect()  # Call reconnect in case of connection loss
                    break
                except json.JSONDecodeError:
                    print(f"JSON decoding error with message: {message}")
                    continue

                # If the message is a pong, reset the timer
                if message == PONG_MESSAGE:
                    print("Received pong")
                    timer.cancel()
                    timer = asyncio.get_event_loop().call_later(30, send_ping, websocket)
                else:
                    message_data = json.loads(message)
                    # Handle the message data as required
                    print(message_data)

    except websockets.exceptions.ConnectionClosed:
        print("Connection was closed unexpectedly")
        await reconnect()


async def reconnect():
    print("Attempting to reconnect...")
    await asyncio.sleep(5)  # Wait for a while before reconnecting
    await connect()  # Reconnect by calling the connect function again


asyncio.run(connect())










