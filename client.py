import asyncio
import websockets
import base64

import gui


async def connect(address):
    async with websockets.connect(address) as websocket:
        window = gui.create_client_window()

        while True:
            event, values = window.read(timeout=1000)

            if event == gui.psg.WIN_CLOSED:
                break

            if event == '-encrypt_text_op-' or event == '-encrypt_file_op-':
                if values['-encrypt_text_op-']:
                    window['-encrypt-'].update(disabled=False)
                    window['-encrypt_into-'].update(disabled=True)
                else:
                    window['-encrypt-'].update(disabled=True)
                    window['-encrypt_into-'].update(disabled=False)
                continue

            if event == '-decrypt_text_op-' or event == '-decrypt_file_op-':
                if values['-decrypt_text_op-']:
                    window['-decrypt-'].update(disabled=False)
                    window['-decrypt_into-'].update(disabled=True)
                else:
                    window['-decrypt-'].update(disabled=True)
                    window['-decrypt_into-'].update(disabled=False)
                continue

            if event == '-encrypt-':
                if values['-encrypt_text_op-']:
                    input_message = bytes(values['-encrypt_message_input-'], 'utf-8')
                    decoded_message = base64.b64encode(input_message).decode("utf-8")
                    message = 'encrypt ' + decoded_message + ' ' + values['-encrypt_password-']
                    await websocket.send(message)
                    response = await websocket.recv()
                    window['-encrypt_result-'].update(value=response)
                continue

            if event == '-encrypt_into-':
                filename = values['-encrypt_input_file-']
                if values['-encrypt_input_file-'] != '':
                    message = 'encrypt '
                    with open(filename, "rb") as file:
                        readed_file = file.read()
                        # Кодируем часть файла в base64 и отправляем как текстовое сообщение
                        encoded_file = base64.b64encode(readed_file).decode("utf-8")
                    message += encoded_file + ' ' + values['-encrypt_password-']

                    await websocket.send(message)
                    response = await websocket.recv()
                    response = bytes(response, 'utf-8')
                    with open(values['-encrypt_into-'], "wb") as file:
                        file.write(response)
                continue

            if event == '-decrypt-':
                if values['-decrypt_text_op-']:
                    message = 'decrypt ' + values['-decrypt_message_input-'] + ' ' + values['-decrypt_password-']
                    await websocket.send(message)
                    response = await websocket.recv()
                    response = base64.b64decode(response).decode('utf-8')
                    result = base64.b64decode(response).decode('utf-8')
                    window['-decrypt_result-'].update(value=result)
                continue

            if event == '-decrypt_into-':
                filename = values['-decrypt_input_file-']
                if values['-decrypt_input_file-'] != '':
                    message = 'decrypt '
                    with open(filename, "rb") as file:
                        readed_file = file.read()
                        # Кодируем часть файла в base64 и отправляем как текстовое сообщение
                        encoded_file = readed_file.decode("utf-8")
                    message += encoded_file + ' ' + values['-decrypt_password-']

                    await websocket.send(message)
                    response = await websocket.recv()
                    response = base64.b64decode(response).decode('utf-8')
                    result_bytes = base64.b64decode(response)
                    with open(values['-decrypt_into-'], "wb") as file:
                        file.write(result_bytes)
                continue

            await websocket.send('ping')
            response = await websocket.recv()
            if response == 'dead':
                break
            continue


if __name__ == "__main__":
    window = gui.create_client_auth_window()

    while True:
        event, values = window.read()

        if event == gui.psg.WIN_CLOSED:
            break

        if event == '-connect-':
            ip = values['-ip_input-']
            port = values['-port_input-']
            path = values['-path_input-']
            address = f'ws://{ip}:{port}{path}'
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(connect(address))
                break
            except:
                pass
