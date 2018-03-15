import time
import socket, select
import logging
import log_config
import threading
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from models import JimAnswer, JimMessage, FilesRepository
from models_repository_serv import Repository, Users, UserContacts, Chat, UsersChat, HistoryMessage

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
            'msg': self.msg,
            'get_contact_list': self.get_contact,
            'add_contact': self.add_contact,
            'del_contact': self.del_contact,
            'add_chat': self.add_chat,
            'exit': self.exit,
            'get_chat_list': self.get_chat_list,
            'login_chat': self.login_chat,
            'chat': self.chat,
            'search_contact':self.search_contact
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
            # history = rep.get_history(account_name)
            # time.sleep(2)
            # for mes in history:
            #     msg = {'action': 'msg',
            #            'time': mes.time_,
            #            'to': mes.to_id,
            #            'from': mes.from_id,
            #            'message': mes.message}
            #     msg = self.msg_client.pack(msg)
            #     sock.send(msg)
            #     print(msg)
            #     time.sleep(1)

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
        msg = {'users': []}
        for username in result:
            msg['users'].append(str(username))
        print(msg)
        msg = self.msg_client.pack(msg)
        sock.send(msg)

        for key, value in self.clients_dict.items():
            if value is sock:
                name_a = key
        history = rep.get_history(name_a)
        for mes in history:
            msg = {'action': 'msg',
                   'time': mes.time_,
                   'to': mes.to_id,
                   'from': mes.from_id,
                   'message': mes.message}
            msg = self.msg_client.pack(msg)
            sock.send(msg)
            print(msg)
            time.sleep(0.2)

    def search_contact(self, *args):
        sock, data = args[0], args[1]
        data = self.msg_client.unpack(data)
        contacts = {'found_users': []}
        for contact in rep.get_all_user():
            if data['contact'].lower() in contact.username.lower():
                contacts['found_users'].append(contact.username)
        contacts = self.msg_client.pack(contacts)
        sock.send(contacts)

    def get_chat_list(self, *args):
        sock = args[0]
        result = rep.get_chat_list()
        msg = self.msg_server.msg('202', len(result))
        msg = self.msg_server.pack(msg)
        sock.send(msg)
        for chatname in result:
            msg = self.msg_client.msg('get_chat_list', str(chatname))
            print(msg)
            msg = self.msg_client.pack(msg)
            sock.send(msg)

    def add_chat(self,*args):
        sock = args[0]
        data = args[1]
        msg = self.msg_client.unpack(data)
        try:
            rep.add(Chat(msg['chat']))
            data = self.msg_server.msg('201')
            data = self.msg_server.pack(data)
            sock.send(data)
        except IntegrityError as err1:
            rep.session.rollback()
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)
        except AttributeError as err2:
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)

    def login_chat(self, *args):
        sock, data, requests = args
        msg = self.msg_client.unpack(data)
        try:
            chat = rep.get_chat(msg['chat'])
            for key, value in self.clients_dict.items():
                if value is sock:
                        name_a = key
            rep.add_user_in_chat(msg['chat'], name_a)
            data = self.msg_server.msg('200')
            data = self.msg_server.pack(data)
            sock.send(data)
        except IntegrityError as err1:
            rep.session.rollback()
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)
        except AttributeError as err:
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)

    def chat(self, *args):
        sock, data, requests = args
        for key, value in self.clients_dict.items():
            if value is sock:
                name_a = key
        id = rep.session.query(Users).filter_by(username = name_a).first().id
        print(id)
        chat_name = rep.session.query(UsersChat).filter_by(user_id = id).first().chat_name
        print(chat_name)
        for user in rep.get_user_in_chat(str(chat_name)):
            print(str(user.user_name))
            self.clients_dict[str(user.user_name)].send(data)


    def msg(self, *args):
        sock, data, requests = args
        msg = self.msg_client.unpack(data)
        if msg['to'] == '':
            requests[sock] = data
        elif rep.get_user(msg['to']) and rep.get_user(msg['to']).flag:
            self.clients_dict[msg['to']].send(data)
        elif rep.get_user(msg['to']) and rep.get_user(msg['to']).flag is False:
            data = self.msg_server.msg('410')
            data = self.msg_server.pack(data)
            sock.send(data)
            rep.add(HistoryMessage(msg['time'], msg['from'], msg['to'], msg['message']))
        else:
            data = self.msg_server.msg('404')
            data = self.msg_server.pack(data)
            sock.send(data)
        print(requests)

    def add_contact(self, *args):
        sock, data = args[0], args[1]
        msg = self.msg_client.unpack(data)
        for key, value in self.clients_dict.items():
            if value is sock:
                name_a = key
        try:
            rep.add_contact(name_a, msg['contact'])
            data = self.msg_server.msg('201')
            data = self.msg_server.pack(data)
            sock.send(data)
        except IntegrityError as err1:
            rep.session.rollback()
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)
        except AttributeError as err2:
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)

    def del_contact(self, *args):
        sock, data = args[0], args[1]
        msg = self.msg_client.unpack(data)
        for key, value in self.clients_dict.items():
            if value is sock:
                name_a = key
        try:
            rep.del_contact(name_a, msg['contact'])
            data = self.msg_server.msg('201')
            data = self.msg_server.pack(data)
            sock.send(data)
        except IntegrityError as err1:
            rep.session.rollback()
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)
        except AttributeError as err2:
            data = self.msg_server.msg('400')
            data = self.msg_server.pack(data)
            sock.send(data)

    def exit(self,*args):
        sock = args[0]
        print('Клиент {} {} откл'.format(sock.fileno(), sock.getpeername()))
        for key, value in self.clients_dict.items():
            if value is sock:
                self.del_user(key, value)
                rep.logout(key)
                try:
                    rep.session.delete(rep.session.query(UsersChat).filter_by(user_id=rep.get_user(key).id).first())
                    rep.session.commit()
                except UnmappedInstanceError:
                    pass
                break

    def read(self, cl):
        requests = {}
        for sock in cl:
            try:
                data = sock.recv(1024)
                msg = self.msg_client.unpack(data)
                print('что то пришло',msg)
                # self.commands[msg['action']](sock, data, requests)
                t = threading.Thread(target= self.commands[msg['action']], args=(sock, data, requests))
                t.start()
            except ConnectionResetError:
                print('Клиент {} {} откл'.format(sock.fileno(), sock.getpeername()))
                for key, value in self.clients_dict.items():
                    if value is sock:
                        self.del_user(key, value)
                        rep.logout(key)
                        try:
                            rep.session.delete(rep.session.query(UsersChat).filter_by(user_id = rep.get_user(key).id).first())
                            rep.session.commit()
                        except UnmappedInstanceError:
                            pass
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
                        print('отправлено')
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

if __name__ == '__main__':
    pass

#разнести функции по разным классам