import time, sys
import socket
import threading

from models import JimMessage, JimAnswer



class Client():

    def __init__(self, username, host, port):
        self._username = username
        # self._password = password
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()


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

    def _send_message(self, sock):
        msg_client = JimMessage(action='msg')
        while True:
            to_ = input('введите ник пользователя которому отправить сообщение или оставьте пустым, если сообщение '
                        'для общего чата')
            data = input('введите текст сообщения')
            if data == 'exit':
                break
            msg_client.from_ = self._username
            msg_client.time
            msg_client.to = to_
            msg_client.message = data
            msg_client.action = 'msg'
            msg = msg_client.msg()
            msg = msg_client.pack(msg)
            sock.send(msg)
            time.sleep(0.5)

    def _get_message(self, sock):
        msg_server = JimMessage()
        while True:
            with self.lock:
                data = sock.recv(1024)
                time.sleep(0.1)
            data = msg_server.unpack(data)
            msg_server.from_ = data['from']
            msg_server.time = data['time']
            msg_server.message = data['message']
            print(data['time'], msg_server.from_, msg_server.message)


    def run(self):

        with self.socket as sock:
            sock.connect((self._host, self._port))
            self.connect_guest()
            t1 = threading.Thread(target=self._send_message, args=(sock,))
            t2 = threading.Thread(target=self._get_message, args= (sock,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

