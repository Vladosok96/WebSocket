import PySimpleGUI as psg


def create_server_window():
    psg.set_options(font=("Arial Bold", 14))

    layout = [
        [
            psg.Column([
                [psg.Text('Сокеты')],
                [psg.Listbox([],
                             size=(30, 15),
                             expand_y=True,
                             enable_events=True,
                             key='-sockets_list-',
                             font=("Arial Bold", 9))]
            ]),
            psg.Column([
                [psg.Button('Закрыть', key='-remove_socket-', disabled=True)]
            ])
        ]
    ]

    return psg.Window('Сети', layout, finalize=True)


def create_client_auth_window():
    psg.set_options(font=("Arial Bold", 14))

    layout = [
        [psg.Text('Подключение к сокету')],
        [psg.Text('ip'), psg.Input(key='-ip_input-', default_text='localhost')],
        [psg.Text('Порт'), psg.Input(key='-port_input-', default_text='8888')],
        [psg.Text('Путь'), psg.Input(key='-path_input-', default_text='/websocket')],
        [psg.Button('Подключиться', key='-connect-')]
    ]

    return psg.Window('Сети', layout, finalize=True)


def create_client_window():
    psg.set_options(font=("Arial Bold", 14))

    layout = [
        [psg.Text('Шифрование')],
        [psg.Text('Сообщение'), psg.Input(key='-encrypt_message_input-')],
        [psg.Text('Выбрать файл'), psg.FileBrowse(change_submits=True, key='-encrypt_input_file-')],
        [psg.Radio('Текст', '-encrypt_radio-', key='-encrypt_text_op-', default=True, enable_events=True),
         psg.Radio('Файл', '-encrypt_radio-', key='-encrypt_file_op-', enable_events=True)],
        [psg.Text('Пароль'), psg.Input(key='-encrypt_password-')],
        [psg.Button('Зашифровать', key='-encrypt-')],
        [psg.SaveAs('Зашифровать в...', key='-encrypt_into-', change_submits=True, disabled=True)],
        [psg.Text('Результат'), psg.Input(disabled=True, key='-encrypt_result-')],
        [psg.HorizontalSeparator()],
        [psg.Text('Дешифрование')],
        [psg.Text('Сообщение'), psg.Input(key='-decrypt_message_input-')],
        [psg.Text('Выбрать файл'), psg.FileBrowse(change_submits=True, key='-decrypt_input_file-')],
        [psg.Radio('Текст', '-decrypt_radio-', key='-decrypt_text_op-', default=True, enable_events=True),
         psg.Radio('Файл', '-decrypt_radio-', key='-decrypt_file_op-', enable_events=True)],
        [psg.Text('Пароль'), psg.Input(key='-decrypt_password-')],
        [psg.Button('Расшифровать', key='-decrypt-')],
        [psg.SaveAs('Расшифровать в...', key='-decrypt_into-', change_submits=True, disabled=True)],
        [psg.Text('Результат'), psg.Input(disabled=True, key='-decrypt_result-')]
    ]

    return psg.Window('Сети', layout, finalize=True)