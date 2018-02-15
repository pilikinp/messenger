import time
import socket, select
import logging
import log_config

from models import JimAnswer, JimMessage, Repository, FilesRepository

class Server(FilesRepository):

    def __init__(self, host = '', port = 7777, clients = 5):
        self._host = host
        self._port = port
        self._sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto = 0)
        self._sock.bind((host, port))
        self._sock.listen(clients)
        self._logger = logging.getLogger('app')
        self.commands = {
            'presence': self.presence,
            'msg': 'msg'
        }
        super().__init__(clients_dict ={}, clients_list =[])

    def presence(self, sock, account_name):

        if account_name in self.clients_dict:
            msg_server = JimAnswer(response= '000')
            msg_server.response = '409'
            msg_server.time = time.time()
            msg_server.alert
            data = msg_server.msg()
            data = msg_server.pack(data)
            sock.send(data)
            self._logger.debug('send error 409')
        else:
            msg_server = JimAnswer(response='000')
            msg_server.response = '200'
            msg_server.time = time.time()
            msg_server.alert
            data = msg_server.msg()
            data = msg_server.pack(data)
            sock.send(data)
            self.add_user(account_name, sock)

    def read(self, cl):
        requests = {}
        for sock in cl:
            try:
                data = sock.recv(1024)
                requests[sock] = data
            except ConnectionResetError:
                print('Клиент {} {} откл'.format(sock.fileno(), sock.getpeername()))
                for key, value in self.clients_dict.items():
                    if value is sock:
                        self.del_user(key, value)
                        break
                print('текущий лист', self.clients_list)
        return requests

    def write(self, requests, cl):
        for sock in self.clients_list:
            if sock in requests:
                resp = requests[sock]
                print(resp)
                for sock in cl:
                    try:
                        sock.send(resp)
                    except ConnectionResetError:
                        pass

    def main_loop(self):
        self._sock.settimeout(0.2)
        while True:
            try:
                sock, addr = self._sock.accept()
            except OSError as e:
                print('timeout вышел')  # timeout вышел
            else:
                msg = sock.recv(2048)
                msg_client = JimMessage(action= 'presence')
                msg = msg_client.unpack(msg)
                print(msg)
                self.commands[msg['action']](sock, msg['user'])
            finally:
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients_list, self.clients_list, [], wait)
                except:
                    pass  # сделать обработку ошибок
                # print(self.clients_list)
                req = self.read(r)
                self.write(req, w)