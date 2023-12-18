import asyncio
import websockets
import base64


async def connect():
    uri = "ws://localhost:8888/websocket"  # Замените на свой адрес веб-сокета
    async with websockets.connect(uri) as websocket:
        print("Соединение установлено")

        while True:
            message = input("Введите сообщение: ")

            if message.split()[0] == 'encrypt':
                filename = message.split()[1]
                password = message.split()[2]
                message = 'encrypt '

                with open(filename, "rb") as file:
                    chunk_size = 1024  # Размер части файла для отправки
                    while True:
                        chunk = file.read(chunk_size)
                        if not chunk:
                            break
                        # Кодируем часть файла в base64 и отправляем как текстовое сообщение
                        encoded_chunk = base64.b64encode(chunk).decode("utf-8")

                        message += encoded_chunk
                message += ' ' + password

            await websocket.send(message)

            if message.split()[0] == 'bye':
                await websocket.close()
                return

            response = await websocket.recv()
            print(f"Получено: {response}")

            if message.split()[0] == 'ping' and response == 'dead':
                await websocket.close()
                return


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect())
