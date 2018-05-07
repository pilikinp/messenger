import sys, time
import json
import socket
import logging
import pickle


class Repository:

    def __init__(self, clients_dict={}, clients_list=[]):
        self.clients_dict = clients_dict
        self.clients_list = clients_list

    def add_user(self, user, sock):
        self.clients_dict[user] = sock
        self.clients_list.append(sock)

    def del_user(self, user, sock):
        del (self.clients_dict[user])
        self.clients_list.remove(sock)


class FilesRepository(Repository):

    def __init__(self, clients_dict={}, clients_list=[]):
        super().__init__(clients_dict, clients_list)
        self._logger = logging.getLogger('app')

    def add_user(self, user, sock):
        super().add_user(user, sock)
        self._logger.info('User {} login'.format(user))

    def del_user(self, user, sock):
        super().del_user(user, sock)
        self._logger.info('User {} logout'.format(user))


class JimMessage():

    def pack(self, msg):
        '''Упаковываем сообщение'''
        # data = json.dumps(msg).encode()
        data = pickle.dumps(msg)
        return data

    def unpack(self, data):
        '''Распаковка сообщения'''
        # data = json.loads(data.decode())
        data = pickle.loads(data)
        return data


class JimAnswer(JimMessage):
    code = {
        '100': 'Базовое уведомление',
        '101': 'Важное уведомление',
        '102': 'В сети',
        '200': 'Ок',
        '201': 'Объект создан',
        '202': 'Подтверждение',
        '400': 'Неправильный запрос/JSON-объект',
        '401': 'Не авторизован',
        '402': 'Не правильный логин/пароль',
        '403': 'Пользователь заблокирован',
        '404': 'Пользователь/чат отсутствует',
        '409': 'Уже имеется подключение с указанным логином',
        '410': 'Адресат существует, но не доступен',
        '500': 'Ошибка сервера'
    }

    def msg(self, code, username=''):
        msg = {'response': code,
               'time': time.ctime(),
               'data':{'alert': self.code[code],
               'user': username}}
        return msg
