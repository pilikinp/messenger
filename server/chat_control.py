import time
import socket, select
import logging
import threading
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from jim.models import JimAnswer, JimMessage, FilesRepository
from repository.models_repository_serv import Repository, Users, Chat, UsersChat, HistoryMessage



class ChatControl():
    rep = Repository()
    msg_server = JimAnswer()
    msg_client = JimMessage()
    client_dict = {}

    def __init__(self):
        self.commands = {
            'presence': self.presence,
            'registration': self.registration,
            'msg': self.msg,
            'get_contact_list': self.get_contact,
            'add_contact': self.add_contact,
            'del_contact': 'self.del_contact',
            'add_chat': 'self.add_chat',
            'exit': 'self.exit',
            'get_chat_list': 'self.get_chat_list',
            'login_chat': 'self.login_chat',
            'chat': 'self.chat',
            'search_contact': self.search_contact
        }

    def presence(self, *args):
        time_, data_recv = args
        account_name, password, avatar, publickey = data_recv['user'], data_recv['password'], data_recv['avatar'], data_recv['publickey']
        ip = self.transport.get_extra_info('peername')
        if rep.get_user(account_name) and rep.get_user(account_name).flag is False and \
                rep.get_user(account_name).password == password:
            rep.login(time_, ip, account_name)
            # self.add_user(account_name, sock)
            self.client_dict[account_name]=self.transport
            print(self.client_dict)

            data = self.msg_server.msg('102', username= account_name)
            data = self.msg_server.pack(data)
            print(data)
            self.transport.write(data)
            print('сообщение отправлено')
            # self._logger.debug('user: {} login'.format(account_name))

        elif rep.get_user(account_name) and rep.get_user(account_name).flag:
            data = self.msg_server.msg('409')
            data = self.msg_server.pack(data)
            self.transport.write(data)
        else:
            data = self.msg_server.msg('402')
            data = self.msg_server.pack(data)
            self.transport.write(data)

    def registration(self, *args):
        time_, data_recv = args
        account_name, password, avatar, publickey = data_recv['user'], data_recv['password'], data_recv['avatar'], \
                                                    data_recv['publickey']
        ip = self.transport.get_extra_info('peername')
        if rep.get_user(account_name) is None:
            rep.add(Users(account_name, password, publickey, avatar))
            rep.login(time_, ip, account_name)
            # self.add_user(account_name, sock)
            self.client_dict[account_name] = self.transport
            print(self.client_dict)

            data = self.msg_server.msg('201')
            data = self.msg_server.pack(data)
            self.transport.write(data)
            # sock.send(b'')
            # self._logger.debug('user: {} login'.format(account_name))
        else:
            data = self.msg_server.msg('409')
            data = self.msg_server.pack(data)
            self.transport.write(data)

    def get_contact(self, *args):
        sock = args[0]
        for key, value in self.client_dict.items():
            if value is self.transport:
                name_a = key
        msg = rep.get_user_contacts(name_a)
        # msg = {'users': []}
        # for username in result:
        #     msg['users'].append(str(username))
        print(msg)
        msg = self.msg_client.pack(msg)
        self.transport.write(msg)

        history = rep.get_history(name_a)
        for mes in history:
            msg = {'action': 'msg',
                   'time': mes.time_,
                   'to': mes.to_id,
                   'from': mes.from_id,
                   'message': mes.message,
                   'flag': mes.flag}
            msg = self.msg_client.pack(msg)
            self.transport.write(msg)
            print(msg)
            time.sleep(0.2)

    def get_name(self):
        for key, value in self.client_dict.items():
            if value is self.transport:
                name_a = key
        return name_a

    def msg(self, *args):
        time, data_recv = args
        print(time, data_recv)
        # msg = self.msg_client.unpack(data)
        if data_recv['to'] == '':
            pass
        elif rep.get_user(data_recv['to']) and rep.get_user(data_recv['to']).flag:
            print('пересылаю сообщение')
            data = {'action': 'msg',
               'time': time,
               'data': data_recv}
            data = self.msg_client.pack(data)
            self.client_dict[data_recv['to']].write(data)
        elif rep.get_user(data_recv['to']) and rep.get_user(data_recv['to']).flag is False:
            print('адресат не в сети')
            data = self.msg_server.msg('410')
            data = self.msg_server.pack(data)
            self.transport.write(data)
            rep.add(HistoryMessage(time, data_recv['from'], data_recv['to'], data_recv['message'], data_recv['flag']))
        else:
            data = self.msg_server.msg('404')
            data = self.msg_server.pack(data)
            self.transport.write(data)


    def add_contact(self, *args):
        data = args[1]
        # msg = self.msg_client.unpack(data)
        for key, value in self.client_dict.items():
            if value is self.transport:
                name_a = key
        try:
            rep.add_contact(name_a, data['contact'])
            data = self.msg_server.msg('201')
            data = self.msg_server.pack(data)
            self.transport.write(data)
        except IntegrityError as err1:
            rep.session.rollback()
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            self.transport.write(data)
        except AttributeError as err2:
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            self.transport.write(data)

    def search_contact(self, *args):
        data = args[1]
        # data = self.msg_client.unpack(data)
        contacts = {'found_users': {}}
        for contact in rep.get_all_user():
            if data['contact'].lower() in contact.username.lower():
                # contacts['found_users'].append(contact.username)
                contacts['found_users']['{}'.format(contact.username)]=['',contact.avatar]
        contacts = self.msg_client.pack(contacts)
        con = self.msg_client.unpack(contacts)
        print('распакованные данные',con)
        self.transport.write(contacts)