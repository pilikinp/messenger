import sys, time
import json
import socket
import logging


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


class JimMessage():

    # action_dict = {
    #     'registration': 'Регистрация',
    #     'presence': 'Присутствие',
    #     'probe': 'проверка присутствия',
    #     'msg': 'простое сообщение пользователю или в чат',
    #     'quit': 'отключение от сервера',
    #     'authenticate': 'авторизация',
    #     'join': 'присоединиться к чата',
    #     'leave': 'покинуть чат'
    # }

    def msg(self, action, username):
        '''Создаем словарь-сообщение для упаковки в JSON'''
        if action == 'presence':
            msg = {'action': action,
                   'time': time.ctime(),
                    'user': username}
        elif action == 'msg':
            to_ = ''
            message = input('Введите сообщение: ')
            msg = {'action': action,
                   'time': time.ctime(),
                   'to': to_,
                   'from': username,
                   'message': message}
        elif action == 'msg_to':
            to_ = input('Введите адресата: ')
            if to_ :
                message = input('Введите сообщение: ')
                msg = {'action': 'msg',
                       'time': time.ctime(),
                       'to': to_,
                       'from': username,
                       'message': message}
            else:
                msg = {'action': 'msg',
                       'time': time.ctime(),
                       'to': username,
                       'from': username,
                       'message': 'Вы не ввели адресата'}
        elif action == 'registration':
            msg = {'action': action,
                   'time': time.ctime(),
                   'user': username}
        elif action == 'get_contact_list':
            msg = {'action': action,
                   'time': time.ctime(),
                   'user': username}
        else:
            sys.exit()
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
        '100': 'Базовое уведомление',
        '101': 'Важное уведомление',
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


    def msg(self, code, quantity = ''):
        msg = {'response': code,
                'time': time.ctime(),
                'alert': self.code[code],
               'quantity': quantity}
        return msg




class Chat:
    '''Пока не понял, что требуется реализовать в данном классе. Может быть функции отправки и получения сообщений,
    а в клиенте оставить только соединение с сервером, но тогда клиент будет наследоваться от чата, а это как то
    неправильно'''
    pass


