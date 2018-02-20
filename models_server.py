import time
import socket, select
import logging
import log_config

from models import JimAnswer, JimMessage, FilesRepository
from models_repository_serv import Repository, Users

rep = Repository()

class Server(FilesRepository):
    msg_server = JimAnswer()
    msg_client = JimMessage()

    def __init__(self, host = '', port = 7777, clients = 5):
        self._host = host
        self._port = port
        self._sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto = 0)
        self._sock.bind((host, port))
        self._sock.listen(clients)
        self._logger = logging.getLogger('app')
        self.commands = {
            'presence': self.presence,
            'registration': self.registration,
            'msg': self.chat,
            'get_contact_list': self.get_contact,
        }
        super().__init__(clients_dict ={}, clients_list =[])

    def presence(self, sock, time_, ip, account_name):
        if rep.get_user(account_name) and rep.get_user(account_name).flag is False:
            rep.login(time_, ip, account_name)
            self.add_user(account_name, sock)
            data = self.msg_server.msg('200')
            data = self.msg_server.pack(data)
            sock.send(data)
            self._logger.debug('user: {} login'.format(account_name))
        elif rep.get_user(account_name) and rep.get_user(account_name).flag:
            data = self.msg_server.msg('409')
            data = self.msg_server.pack(data)
            sock.send(data)
        else:
            data = self.msg_server.msg('402')
            data = self.msg_server.pack(data)
            sock.send(data)

    def registration(self, sock, time_, ip, account_name):
        if rep.get_user(account_name) is None:
            rep.add(Users(account_name))
            rep.login(time_, ip, account_name)
            self.add_user(account_name, sock)
            data = self.msg_server.msg('200')
            data = self.msg_server.pack(data)
            sock.send(data)
            self._logger.debug('user: {} login'.format(account_name))
        else:
            data = self.msg_server.msg('409')
            data = self.msg_server.pack(data)
            sock.send(data)

    def get_contact(self, *args):
        sock = args[0]
        for key, value in self.clients_dict.items():
            if value is sock:
                name_a = key
        result = rep.get_user_contacts(name_a)
        msg = self.msg_server.msg('202', len(result))
        msg = self.msg_server.pack(msg)
        sock.send(msg)
        for username in result:
            msg = self.msg_client.msg('get_contact_list', str(username))
            msg = self.msg_client.pack(msg)
            sock.send(msg)

    def chat(self, *args):
        sock, data, msg, requests = args
        if msg['to'] == '':
            requests[sock] = data
        elif rep.get_user(msg['to']) and rep.get_user(msg['to']).flag:
            self.clients_dict[msg['to']].send(data)
        elif rep.get_user(msg['to']) and rep.get_user(msg['to']).flag is False:
            data = self.msg_server.msg('410')
            data = self.msg_client.pack(data)
            sock.send(data)
        else:
            data = self.msg_server.msg('404')
            data = self.msg_client.pack(data)
            sock.send(data)
        print(requests)

    def read(self, cl):
        requests = {}
        for sock in cl:
            try:
                data = sock.recv(1024)
                msg = self.msg_client.unpack(data)
                print(self.msg_client)
                self.commands[msg['action']](sock, data, msg, requests)
                # if msg['to'] == '':
                #     requests[sock] = data
                # elif rep.get_user(msg['to']) and rep.get_user(msg['to']).flag:
                #     self.clients_dict[msg['to']].send(data)
                # elif rep.get_user(msg['to']).flag is False:
                #     data = self.msg_server.msg('410')
                #     data = self.msg_client.pack(data)
                #     sock.send(data)
                # else:
                #     data = self.msg_server.msg('404')
                #     data = self.msg_client.pack(data)
                #     sock.send(data)
                # print(requests)
            except ConnectionResetError:
                print('Клиент {} {} откл'.format(sock.fileno(), sock.getpeername()))
                for key, value in self.clients_dict.items():
                    if value is sock:
                        self.del_user(key, value)
                        rep.logout(key)
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
                pass
                # print('timeout вышел')  # timeout вышел
            else:
                msg = sock.recv(2048)
                msg = self.msg_client.unpack(msg)
                print(msg)
                self.commands[msg['action']](sock, msg['time'], addr, msg['user'])
                # msg = sock.recv(2048)
                # msg = self.msg_client.unpack(msg)
                # self.commands[msg['action']](sock)
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
