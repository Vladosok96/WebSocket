import PySimpleGUI as psg


def create_window():
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