from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Text, BLOB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    login = Column(String, primary_key= True)
    name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    avatar = Column(BLOB)

    def __init__(self, login, name = None, last_name = None, email = None, phone = None, avatar = None):
        self.login = login
        self.name = name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.avatar = avatar


class Contacts(Base):
    __tablename__ = 'Contacts'
    id = Column(Integer, primary_key= True)
    contact_name = Column(String)
    publickey = Column(String)
    avatar = Column(BLOB)

    def __init__(self, contact_name, publickey, avatar = b'ava.png'):
        self.contact_name = contact_name
        self.publickey = publickey
        self.avatar = avatar

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
        self.engine = create_engine('sqlite:///repository/db_client/{}.db?check_same_thread=False'.format(name))
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

    def add_contact(self, name, publickey, avatar):
        self.session.add(Contacts(name, publickey, avatar= avatar))

    def del_model(self, model):
        models = self.session.query(model)
        for mod in models:
            self.session.delete(mod)
        self.session.commit()

    def contacts_list(self):
        return self.session.query(Contacts).all()

    def get_contact(self, name):
        return self.session.query(Contacts).filter(Contacts.contact_name == name).first()

    def get_avatar(self):
        return self.session.query(User).all()[0].avatar

    def get_avatar_contact(self, username):
        return self.session.query(Contacts).filter(Contacts.contact_name == username).first().avatar

    def get_history(self, name , username):
        return self.session.query(HistoryMessage).filter(((HistoryMessage.to_id == name) & (HistoryMessage.from_id == username)) | ((HistoryMessage.to_id == username) & (HistoryMessage.from_id == name))).all()
        # Исправить поиск истории пока ищет только сообщения написанные только клиентом, сообщения для него не ищет

    def get_publickey(self,name):
        return self.session.query(Contacts).filter(Contacts.contact_name == name).first().publickey

if __name__ == '__main__':
    rep = Repository('pilik23')
    # with open('ava.png', 'rb') as f:
    #     file = f.read()
    # rep.add_obj(User('pilik22', avatar= file))
    # rep.del_model(Contacts)
    # print(rep.contacts_list())
    # for i in range(10):
    #     rep.add_contact('pilik{}'.format(i))
    # print(rep.get_history('pilik26')[0].message)
    print(rep.get_avatar())
