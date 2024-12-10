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
apiKey = 'bg_660c4bcf9e0a9483ce711e0dbbf4c595'
passphrase = 'QWERTYasdfg808801'
secretKey = '6bc9b6713cb3c34f93b88aeac43998d665979ea2c301c4b5e51821b7a79ce511'


def send_ping(websocket):
    asyncio.get_event_loop().create_task(websocket.send(PING_MESSAGE))
    print('send ping')


async def connect():
    uri = "wss://ws.bitget.com/mix/v1/stream"
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
                print(f"Authentication error code: {auth_response['code']}")
                return

            # Subscribe to the orders channel
            orders_request = {
                "op": "subscribe",
                "args": [{
                    "channel": "orders",
                    "instType": "UMCBL",
                    "instId": "default"
                }]
            }
            await websocket.send(json.dumps(orders_request))
            order_response = json.loads(await websocket.recv())
            print(order_response)

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










