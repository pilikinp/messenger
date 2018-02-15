import time, sys
import socket

from models import JimMessage, JimAnswer



class Client():

    def __init__(self, username, host, port):
        self._username = username
        # self._password = password
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    @property
    def socket(self):
        return self._sock

    def connect_guest(self):

        msg_client = JimMessage(action='presence')
        print(msg_client.user)
        msg_client.user = (self._username)
        data = msg_client.msg()
        # print(data)
        self.socket.send(msg_client.pack(data))
        msg_server = JimAnswer(response='000')
        msg_recv = self.socket.recv(1024)
        msg_recv = msg_server.unpack(msg_recv)
        print(msg_recv)
        msg_server.response = msg_recv['response']
        msg_server.time = msg_recv['time']

        if msg_server.response == '200':
            print(msg_server.alert)
        elif msg_server.response == '409':
            print(msg_server.alert)
            sys.exit()
        else:
            print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_server.response))
            sys.exit()

    def _send_message(self):
        with self.socket as sock:
            sock.connect((self._host, self._port))
            self.connect_guest()
            msg_client = JimMessage(action='msg')

            while True:
                data = input('Ваше сообщение: ')
                if data == 'exit':
                    break
                msg_client.from_ = self._username
                msg_client.time
                msg_client.message = data
                msg_client.action = 'msg'
                msg = msg_client.msg()
                msg = msg_client.pack(msg)
                sock.send(msg)

    def _get_message(self):
        with self.socket as sock:
            sock.connect((self._host, self._port))
            self.connect_guest()
            msg_server = JimMessage()
            while True:
                data = sock.recv(1024)
                data = msg_server.unpack(data)
                msg_server.from_ = data['from']
                msg_server.time = data['time']
                msg_server.message = data['message']
                print(data['time'], msg_server.from_, msg_server.message)