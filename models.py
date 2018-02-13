import time
import json
import socket
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

    def __init__(self):
        self._action = None
        self._time = None
        self._to = None
        self._from = None
        self._message = None
        self._encoding = 'ancii'
        # self._status = None
        self._user = None

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
        if value in []:
            self._to = value
        else:
            print('Пользователя с таким именем нет')

    @property
    def from_(self):
        return self._from

    @property
    def message(self):
        return self._message

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
    def user(self, user):
        self._user = {}
        self.user['account_name'], self.user['status'] = user

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


class JimAnswer(JimMessage):

    code = {
        100: 'Базовое уведомление',
        101: 'Важное уведомление',
        200: 'Ок',
        201: 'Объект создан',
        202: 'Подтверждение',
        400: 'Неправильный запрос/JSON-объект',
        401: 'Не авторизован',
        402: 'Не правильный логин/пароль',
        403: 'Пользователь заблокирован',
        404: 'Пользователь/чат отсутствует на месте',
        409: 'Уже имеется подключение с указанным логином',
        410: 'Адресат существует, но не доступен',
        500: 'Ошибка сервера'
    }

    def __init__(self):
        self._response = None
        self._time = None
        self._alert = None

    @property
    def response(self):
        return self._response

    @response.setter
    def responce(self, value):
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
        self._alert = self.code[self._alert]
        return self._alert

    def msg(self):
        msg = {'responce': self.response,
                'time': self.time,
                'alert': self.alert}
        return msg

    def pack(self):
        return super(JimAnswer, self).pack()

    def unpack(self, data):
        data = super(JimAnswer, self).unpack(data)
        self.response = data['responce']



class Client:

    def __init__(self, username, host, port):
        self._username = username
        # self._password = password
        self._host = host
        self._port = port
        self._sock = socket.socket()
        self._sock.connect((str(host), int(port)))

    @property
    def socket(self):
        return self._sock

    def connect_guest(self, sock, account_name, status='Yep, I am here'):

        msg_client = JimMessage
        msg_client.action = 'presence'
        msg_client.user = (account_name, status)
        data = msg_client.msg()
        sock.send(msg_client.pack(data))
        msg_server = JimAnswer
        msg_recv = sock.recv(1024)
        msg_recv = msg_server.unpack(msg_recv)
        msg_server.response = msg_recv['responce']
        msg_server.time = msg_recv['time']
        msg_server.alert

        if msg_server.responce == '200':
            print(msg_server.alert)
        elif msg_server.response == '409':
            print(msg_server.alert)
            sys.exit()
        else:
            print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_server.response))
            sys.exit()

    def chat(addr, port, account_name):
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.connect((addr, port))
            connect_guest(sock, account_name)
            msg_client = {
                'action': 'msg',
                'time': '',
                'to': 'account_name',
                'from': 'account_name',
                'encoding':'ascii',
                'message':''
            }
            while True:
                data = input('Ваше сообщение: ')
                if data == 'exit':
                    break
                msg_client['from'] = account_name
                msg_client['time'] = time.time()
                msg_client['message'] = data
                msg = json.dumps(msg_client).encode()
                sock.send(msg)

    def chat2(addr, port, account_name):
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.connect((addr, port))
            connect_guest(sock, account_name)
            while True:
                data = sock.recv(1024)
                msg_serv = json.loads(data.decode())
                print(msg_serv['time'], msg_serv['from'], msg_serv['message'])


class Chat:
    pass


