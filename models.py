import sys, time
import json
import socket
import logging



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


class Chat:
    '''Пока не понял, что требуется реализовать в данном классе. Может быть функции отправки и получения сообщений,
    а в клиенте оставить только соединение с сервером'''
    pass


class Repository:

    def __init__(self, clients_dict = {}, clients_list = [] ):
        self.clients_dict = clients_dict
        self.clients_list = clients_list

    def add_user(self, user, sock):
        self.clients_dict[user] = sock
        self.clients_list.append(sock)

    def del_user(self, user, sock):
        del(self.clients_dict[user])
        self.clients_list.remove(sock)

class FilesRepository(Repository):

    def __init__(self, clients_dict = {}, clients_list =[]):
        super().__init__(clients_dict, clients_list)
        self._logger = logging.getLogger('app')

    def add_user(self, user, sock):
        super().add_user(user,sock)
        self._logger.info('User {} login'.format(user))

    def del_user(self, user, sock):
        super().del_user(user, sock)
        self._logger.info('User {} logout'.format(user))
