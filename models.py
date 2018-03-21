import sys, time
import json
import socket
import logging


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

    # def msg(self, *args):
    #     msg = {'action': args[0],
    #         'time': time.ctime(),
    #         'user': args[1],
    #         'to': args[2],
    #         'from': args[3],
    #         'message': args[4],
    #         'contact': args[5],
    #         'chat': args[6]}
    #
    #     if action == 'presence':
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username}
    #     elif action == 'msg':
    #         to_ = ''
    #         message = input('Введите сообщение: ')
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'to': to_,
    #                'from': username,
    #                'message': message}
    #     elif action == 'msg_to':
    #         to_ = input('Введите адресата: ')
    #         if to_:
    #             message = input('Введите сообщение: ')
    #             msg = {'action': 'msg',
    #                    'time': time.ctime(),
    #                    'to': to_,
    #                    'from': username,
    #                    'message': message}
    #         else:
    #             msg = {'action': 'msg',
    #                    'time': time.ctime(),
    #                    'to': username,
    #                    'from': username,
    #                    'message': 'Вы не ввели адресата'}
    #     elif action == 'registration':
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username}
    #     elif action == 'get_contact_list':
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username}
    #     elif action == 'get_chat_list':
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username}
    #     elif action == 'add_contact':
    #         contact = input('Введите имя контакта: ')
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username,
    #                'contact': contact}
    #     elif action == 'del_contact':
    #         contact = input('Введите имя контакта: ')
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username,
    #                'contact': contact}
    #     elif action == 'exit':
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username}
    #     elif action == 'add_chat':
    #         chat = input('Введите название чата: ')
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username,
    #                'chat': chat}
    #     elif action == 'login_chat':
    #         chat = input('Введите название чата: ')
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'user': username,
    #                'chat': chat}
    #     elif action == 'chat':
    #         message = input('Введите сообщение: ')
    #         msg = {'action': action,
    #                'time': time.ctime(),
    #                'to': '',
    #                'from': username,
    #                'message': message}
    #     else:
    #         sys.exit()
    #     return msg

    # сделать одно универсальное сообщение

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
               'alert': self.code[code],
               'user': username}
        return msg
