import sys, time
import json
import socket, select
import logging

from lib_decoratorr import log
# from socket import *


class JimMessage:

    action_dict = {
        'presence': 'Присутствие',
        'probe': 'проверка присутствия',
        'msg': 'простое сообщение пользователю или в чат',
        'quit': 'отключение от сервера',
        'authenticate': 'авторизация',
        'join': 'присоединиться к чата',
        'leave': 'покинуть чат'
    }

    def __init__(self, action = 'action', time = time.ctime(), to = '', from_ = '', message = '', user = ''):
        self._action = action
        self._time = time
        self._to = to
        self._from = from_
        self._message = message
        self._encoding = 'ancii'
        # self._status = None
        self._user = user

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):

        if value in self.action_dict:
            print('записываю')
            self._action = value
        else:
            print('Не правильно задана команда')

    @property
    def time(self):
        self._time = time.ctime()
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, value):
        if value in ['']:
            self._to = value
        else:
            print('Пользователя с таким именем нет')

    @property
    def from_(self):
        return self._from

    @from_.setter
    def from_(self, value):
        self._from = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    # @property
    # def status(self):
    #     return self._status
    #
    # @status.setter
    # def status(self, value):
    #     self._status = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    def msg(self):
        '''Создаем словарь-сообщение для упаковки в JSON'''
        if self.action == 'presence':
            msg = {'action': self.action,
                   'time': self.time,
                    'user': self.user}
        elif self.action == 'msg':
            msg = {'action': self.action,
                   'time': self.time,
                   'to': self.to,
                   'from': self.from_,
                   'encoding': self._encoding,
                   'message': self.message}
        return msg

    def pack(self, msg):
        '''Упаковываем сообщение'''
        data = json.dumps(msg).encode()
        return data

    def unpack(self, data):
        '''Распаковка сообщения'''
        data = json.loads(data.decode())
        return data


class JimAnswer():

    code = {
        '100': 'Базовое уведомление',
        '101': 'Важное уведомление',
        '200': 'Ок',
        '201': 'Объект создан',
        '202': 'Подтверждение',
        '400': 'Неправильный запрос/JSON-объект',
        '401': 'Не авторизован',
        '402': 'Не правильный логин/пароль',
        '403': 'Пользователь заблокирован',
        '404': 'Пользователь/чат отсутствует на месте',
        '409': 'Уже имеется подключение с указанным логином',
        '410': 'Адресат существует, но не доступен',
        '500': 'Ошибка сервера'
    }

    def __init__(self, response = '000', time = time.ctime(), alert = ''):
        self._response = response
        self._time = time
        self._alert = alert

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        if value in self.code:
            self._response = value
        else:
            print('Нет такого кода')

    @property
    def time(self):
        self._time = time.ctime()
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def alert(self):
        self._alert = self.code[self._response]
        return self._alert

    def msg(self):
        msg = {'response': self.response,
                'time': self.time,
                'alert': self.alert}
        return msg

    # def pack(self):
    #     return super().pack()
    #
    # def unpack(self, data):
    #     msg = super().unpack(data)
    #     self.response = msg['responce']
    def pack(self, msg):
        '''Упаковываем сообщение'''
        data = json.dumps(msg).encode()
        return data

    def unpack(self, data):
        '''Распаковка сообщения'''
        msg = json.loads(data.decode())
        return msg



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


class Chat:
    '''Пока не понял что требуется реализовать в данном классе. Может быть функции отправки и получения сообщений'''
    pass

class Server():

    clients = {}
    clients_list = []
    msg_server = {
        'response': '',
        'time': '',
        'allert': ''
    }


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




    @log
    def presence(self, sock, account_name):

        if account_name in self.clients:
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
            self.clients_list.append(sock)
            self._logger.debug('send presence')


    # def msg(sock, to, from_, message):
    #
    #     if to in clients:
    #         data = json.dumps(message).encode()
    #         clients[to].send(data)
    #     else:
    #         msg_server['responce'] = '404'
    #         msg_server['allert'] = 'Not found'
    #         msg_server['time'] = time.time()
    #         data = json.dumps(msg_server).encode()
    #         sock.send(data)

    def read(self, cl):
        requests = {}
        for sock in cl:
            try:
                data = sock.recv(1024)
                requests[sock] = data
            except:  # конкретизировать исключение возникающее при отключении клиента
                print('Клиент {} {} откл'.format(sock.fileno(), sock.getpeername()))
                self._logger.warning('client logout {} {}'.format(sock.fileno(), sock.getpeername()))
                self.clients_list.remove(sock)
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
                    except:  # конкретизировать исключение возникающее при отключении клиента
                        print('Клиент {} отключился'.format(sock.fileno()))
                        self._logger.warning('client logout {} {}'.format(sock.fileno(), sock.getpeername()))
                        self.clients_list.remove(sock)

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
                print(self.clients_list)
                req = self.read(r)
                self.write(req, w)

    # def rec(sock):
    #     while True:
    #         msg = sock.recv(2048)
    #         msg = json.loads(msg.decode())
    #         commands[msg['action']](sock, msg['to'],msg['from'], msg['message'])
