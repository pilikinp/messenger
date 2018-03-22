import sqlite3
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData, ForeignKey, Text
from models_repository_serv import Repository, Users, UserContacts
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

import time

Base = declarative_base()


class Contacts(Base):
    __tablename__ = 'Contacts'
    id = Column(Integer, primary_key= True)
    contact_name = Column(String)
    publickey = Column(String)

    def __init__(self, contact_name, publickey):
        self.contact_name = contact_name
        self.publickey = publickey

    def __repr__(self):
        return self.contact_name

class HistoryMessage(Base):
    __tablename__ = 'HistoryMessage'
    id = Column(Integer, primary_key= True)
    time_ = Column(String)
    from_id = Column(String, ForeignKey('Contacts.id'))
    to_id = Column(String, ForeignKey('Contacts.id'))
    message = Column(Text)

    def __init__(self, time_, from_id, to_id, message):
        self.time_ = time_
        self.from_id = from_id
        self.to_id = to_id
        self.message = message

class Repository():

    def __init__(self, name):
        self.engine = create_engine('sqlite:///{}.db?check_same_thread=False'.format(name))
        self.session = self.get_session()
        self.create_base()

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def create_base(self):
        Base.metadata.create_all(self.engine)

    def add_obj(self, obj):
        self.session.add(obj)
        print('обавляем объект')
        self.session.commit()

    def add_contact(self, name, publickey):
        self.session.add(Contacts(name, publickey))

    def del_model(self, model):
        models = self.session.query(model)
        for mod in models:
            self.session.delete(mod)
        self.session.commit()

    def contacts_list(self):
        return self.session.query(Contacts).all()

    def get_history(self, name , username):
        return self.session.query(HistoryMessage).filter(((HistoryMessage.to_id == name) & (HistoryMessage.from_id == username)) | ((HistoryMessage.to_id == username) & (HistoryMessage.from_id == name))).all()
        # Исправить поиск истории пока ищет только сообщения написанные только клиентом, сообщения для него не ищет

    def get_publickey(self,name):
        return self.session.query(Contacts).filter(Contacts.contact_name == name).first().publickey

if __name__ == '__main__':
    rep = Repository('pilik22')
    # rep.add_obj(Contacts('pilik22'))
    # rep.del_model(Contacts)
    print(rep.contacts_list())
    # for i in range(10):
    #     rep.add_contact('pilik{}'.format(i))
    # print(rep.get_history('pilik26')[0].message)