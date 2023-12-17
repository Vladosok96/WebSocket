import asyncio
import websockets


async def connect():
    uri = "ws://localhost:8888/websocket"  # Замените на свой адрес веб-сокета
    async with websockets.connect(uri) as websocket:
        print("Соединение установлено")

        while True:
            message = input("Введите сообщение: ")

            if message == 'test':
                message = 'encrypt aaaaaaaaaaaaaa\x10sssssssss'

            await websocket.send(message)
            print(f"Отправлено: {message}")

            if message.split()[0] == 'bye':
                await websocket.close()
                return

            response = await websocket.recv()
            print(f"Получено: {response}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect())
