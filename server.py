import tornado.ioloop
import tornado.web
import tornado.websocket

import gui

import threading
import struct
import base64

import DES

client_counter = 1


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")  # Создайте HTML-файл для отображения страницы


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    connected_clients = {}

    def open(self):
        global client_counter

        self.client_id = client_counter
        self.alive = True
        client_counter += 1

        WebSocketHandler.connected_clients[self.client_id] = self

        print(f"WebSocket открыт c id: {self.client_id}")

    def on_message(self, message):
        print(message)
        split_message = message.split()

        if split_message[0].lower() == 'ping':
            if self.alive == False:
                self.write_message('dead')
                self.close()
                return
            self.write_message('alive')

        elif split_message[0].lower() == 'bye':
            self.write_message(f"bye variant {self.client_id}")
            self.close()

        elif split_message[0].lower() == 'hello':
            self.client_id = int(split_message[1])
            self.write_message(f"hello variant {self.client_id}")

        elif split_message[0].lower() == 'encrypt':
            file_blocks = []
            output_file_blocks = []
            password = split_message[2]

            # Чтение сообщения и разделение на блоки по 64 бит
            i = 0
            while True:
                file_block = bytes(split_message[1][i:(i+8)], 'utf-8')
                if len(file_block) == 0:
                    break
                if len(file_block) < 8:
                    file_block += b'\x00' * (8 - len(file_block))
                int_file_block = struct.unpack('Q', file_block)[0]
                file_blocks.append(int_file_block)
                i += 8

            # Чтение пароля перевод в 7-ми байтовое число
            password = bytes(password[:7], 'utf-8')
            int_password = int.from_bytes(password, 'big')

            # Применение функции шифрования DES на каждый блок в отдельности (ECB)
            progress = 0
            for block in file_blocks:
                encrypted_block = DES.DES(block, int_password, DES.ENCRYPTION)
                output_file_blocks.append(encrypted_block)
                progress += 1
                print(f'processing: {progress}/{len(file_blocks)}')

            # Вывод в файл
            output = b''
            for block in output_file_blocks:
                packed_data = struct.pack('Q', block)
                output += packed_data

            base64_data = base64.b64encode(output)
            self.write_message(base64_data.decode('utf-8'))

        elif split_message[0].lower() == 'decrypt':
            file_blocks = []
            output_file_blocks = []
            password = split_message[2]

            # Чтение сообщения и разделение на блоки по 64 бит
            bytes_data = base64.b64decode(split_message[1])
            i = 0
            while True:
                file_block = bytes_data[i:(i + 8)]
                if len(file_block) == 0:
                    break
                if len(file_block) < 8:
                    file_block += b'\x00' * (8 - len(file_block))
                int_file_block = struct.unpack('Q', file_block)[0]
                file_blocks.append(int_file_block)
                i += 8

            # Чтение пароля перевод в 7-ми байтовое число
            password = bytes(password[:7], 'utf-8')
            int_password = int.from_bytes(password, 'big')

            # Применение функции шифрования DES на каждый блок в отдельности (ECB)
            progress = 0
            for block in file_blocks:
                encrypted_block = DES.DES(block, int_password, DES.DECRYPTION)
                output_file_blocks.append(encrypted_block)
                progress += 1
                print(f'processing: {progress}/{len(file_blocks)}')

            # Вывод в файл
            output = b''
            for block in output_file_blocks:
                packed_data = struct.pack('Q', block)
                output += packed_data

            base64_data = base64.b64encode(output)
            self.write_message(base64_data.decode('utf-8'))


        else:
            print(message)
            self.write_message(message)

    def on_close(self):
        print("WebSocket закрыт")
        for i in WebSocketHandler.connected_clients:
            if WebSocketHandler.connected_clients[i].client_id == self.client_id:
                del WebSocketHandler.connected_clients[i]
                break


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/websocket', WebSocketHandler)
    ], websocket_message_max_size=104857600)


def start_tornado():
    app = make_app()
    app.listen(8888)
    print("Сервер запущен на порту 8888")
    tornado.ioloop.IOLoop.instance().start()


def gui_thread():
    window = gui.create_server_window()
    last_client_list = []
    while True:
        event, values = window.read(timeout=10)

        if event in (gui.psg.WIN_CLOSED, 'Exit'):
            break

        if event == '-remove_socket-':
            websocket_handler = WebSocketHandler.connected_clients.get(int(values['-sockets_list-'][0]))
            if websocket_handler:
                websocket_handler.alive = False
            window['-remove_socket-'].update(disabled=True)

        if event == '-sockets_list-':
            if len(values['-sockets_list-']) > 0:
                window['-remove_socket-'].update(disabled=False)

        client_list = []
        for client in WebSocketHandler.connected_clients:
            client_list.append(WebSocketHandler.connected_clients[client].client_id)
        if client_list != last_client_list:
            window['-sockets_list-'].update(values=client_list)
            last_client_list = client_list.copy()


if __name__ == "__main__":
    tornado_task = threading.Thread(target=start_tornado)
    tornado_task.start()
    gui_task = threading.Thread(target=gui_thread)
    gui_task.start()
    tornado_task.join()
