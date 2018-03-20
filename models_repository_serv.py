from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, Boolean, ForeignKey, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

CBase = declarative_base()

class Users(CBase):

    __tablename__ = 'users'
    id = Column(Integer(), primary_key= True)
    username = Column(Unicode(), nullable= False, unique= True)
    # socket = Column(BLOB)
    flag = Column(Boolean())

    def __init__(self, username, flag = 0):
        self.username = username
        self.flag = flag

    def __repr__(self):
        return self.username


class HistoryUsers(CBase):

    __tablename__ = 'history_users'
    id = Column(Integer(), primary_key= True)
    time = Column(Unicode())
    id_user = Column(Integer(), ForeignKey('users.id'))

    p_id_user = relationship('Users', foreign_keys = [id_user])

    def __init__(self, time_, ip, id):
        self.time=time_
        self.ip = ip
        self.id_user = id

class HistoryMessage(CBase):
    __tablename__ = 'HistoryMessage'
    id = Column(Integer, primary_key=True)
    time_ = Column(String)
    from_id = Column(String)
    to_id = Column(String)
    message = Column(String)

    def __init__(self, time_, from_id, to_id, message):
        self.time_ = time_
        self.from_id = from_id
        self.to_id = to_id
        self.message = message



class UserContacts(CBase):

    __tablename__ = 'user_contacts'
    id = Column(Integer(), primary_key=True)
    id_user = Column(Integer(), ForeignKey('users.id'))
    id_contact = Column(Integer(), ForeignKey('users.id'))

    # name_user = relationship('Users', order_by = Users.id)
    # name_contact = relationship('Users', order_by = Users.id)

    # check_1 = UniqueConstraint('id_user', 'id_contact') не работает если при создании таблиц не задавать UNIQUE
    user_name = relationship('Users', foreign_keys=[id_user])
    contact_name = relationship('Users', foreign_keys=[id_contact])

    def __init__(self, id_user, id_contact):
        self.id_user = id_user
        self.id_contact = id_contact

    def __repr__(self):
        return '{}'.format(self.contact_name)

class Chat(CBase):
    __tablename__ = 'Chat'
    id = Column(Integer(), primary_key= True)
    chat_name = Column(String(), unique= True)

    def __init__(self, chat_name):
        self.chat_name = chat_name

    def __repr__(self):
        return '{}'.format(self.chat_name)

class UsersChat(CBase):
    __tablename__ = 'UsersChat'
    id = Column(Integer(), primary_key= True)
    chat_id = Column(Integer(), ForeignKey('Chat.id'))
    user_id = Column(Integer(), ForeignKey('users.id'))

    chat_name = relationship('Chat', foreign_keys= [chat_id])
    user_name = relationship('Users', foreign_keys= [user_id])

    def __init__(self, chat_id, user_id):
        self.chat_id = chat_id
        self.user_id = user_id

    def __repr__(self):
        return '{}'.format(self.chat_name)

class Repository:

    def __init__(self):
        self.engine = create_engine(('sqlite:///server_db.db?check_same_thread=False'))
        self.session = self.get_session()
        self.create_base()

    def create_base(self):
        CBase.metadata.create_all(self.engine)

    def get_session(self):
        Session = sessionmaker(bind= self.engine)
        session = Session()
        return session

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()

    def del_users(self, username):
        pass

    def get_history(self, username):
        result = self.session.query(HistoryMessage).filter(HistoryMessage.to_id == username).all()
        for i in self.session.query(HistoryMessage).filter(HistoryMessage.to_id == username).all():
            self.session.delete(i)
        self.session.commit()
        return result


    def update_users(self, username_old, username):
        pass

    def get_all_user(self):
        return self.session.query(Users).all()

    def get_user(self, username):
        result = self.session.query(Users).filter_by(username = username).first()
        return result

    def get_contact(self, username, contact):
        # contacts = self.get_user_contacts(username)
        id = self.get_user(username).id
        id_cont = self.get_user(contact).id
        result = self.session.query(UserContacts).filter_by(id_user= id).filter_by(id_contact= id_cont).first()
        return result

    def create_chat(self, chat_name):
        self.add(Chat(chat_name))

    def get_chat_list(self, name_a):
        id = self.get_user(name_a).id
        result = self.session.query(UsersChat).filter(UsersChat.user_id == id).all()
        return result

    def get_chat(self, chat_name):
        result = self.session.query(Chat).filter_by(chat_name = chat_name).first()
        return result

    def get_user_in_chat(self, chat_name):
        id = self.session.query(Chat).filter_by(chat_name=chat_name).first().id
        result = self.session.query(UsersChat).filter_by(chat_id=id).all()
        return result

    def add_contact(self, acountname, contact_name):
        id = self.session.query(Users).filter_by(username=acountname).first().id
        id_contact = self.session.query(Users).filter_by(username=contact_name).first().id
        self.add(UserContacts(id, id_contact))

    def del_contact(self, acountname, contact_name):
        result = self.get_contact(acountname,contact_name)
        self.session.delete(result)
        self.session.commit()

    def login(self, time_, ip, username):
        result = self.session.query(Users).filter_by(username=username).first()
        result.flag = 1
        # result.socket = sock
        self.session.add(HistoryUsers(time_, ip, result.id))
        self.session.commit()

    def logout(self, username):
        result = self.session.query(Users).filter_by(username=username).first()
        result.flag = 0
        self.session.commit()

    def get_user_contacts(self,user_name):
        id = self.session.query(Users).filter_by(username= user_name).first().id
        result = self.session.query(UserContacts).filter_by(id_user= id).all()
        return result

    def add_user_in_chat(self, chat, username):
        chat_id = self.session.query(Chat).filter_by(chat_name = chat).first().id
        user_id = self.session.query(Users).filter_by(username = username).first().id
        self.session.add(UsersChat(chat_id, user_id))
        self.session.commit()

if __name__ == '__main__':
    rep = Repository()
    # rep.logout('pilik')
    # print(rep.get_user('pilik').flag is False)
    # rep.add(UserContacts(1,3))
    # rep.add(Users('pilik5'))
    # print(rep.get_user('pilik5'))
    # print(rep.get_user_contacts('pilik14'))
    #
    # print(rep.get_user_contacts('pilik14'))
    # result = rep.get_user_contacts('pilik14')
    # print(rep.session.query(UserContacts).get(2).id_user)
    # print(rep.session.query(UserContacts).get(2).contact_name)
    # # print(rep.session.query(Users).get(18).contacts)
    # for i in rep.get_chat_list():
    #     print('room' == str(i))
    # print(rep.get_chat_list())
    # print('room' in rep.get_chat_list())
    # for i in rep.get_user_in_chat('room'):
    #     print(i.user_name)
    # print(rep.session.query(UsersChat).filter_by(user_id =12).first())
    # rep.session.delete(rep.session.query(UsersChat).filter_by(user_id=rep.get_user('pilik1').id).first())
    # rep.session.commit()
    print(rep.get_chat_list('pilik2'))