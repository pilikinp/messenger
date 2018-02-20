from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Unicode, UniqueConstraint, Boolean, ForeignKey, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

CBase = declarative_base()

class Users(CBase):

    __tablename__ = 'users'
    id = Column(Integer(), primary_key= True)
    username = Column(Unicode(), unique= True)
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


class UserContacts(CBase):

    __tablename__ = 'user_contacts'
    id = Column(Integer(), primary_key=True)
    id_user = Column(Integer(), ForeignKey('users.id'))
    id_contact = Column(Integer(), ForeignKey('users.id'))

    # check_1 = UniqueConstraint('id_user', 'id_contact') не работает если при создании таблиц не задавать UNIQUE

    def __init__(self, id_user, id_contact):
        self.id_user = id_user
        self.id_contact = id_contact

    p_id_users = relationship('Users', foreign_keys = [id_user])
    p_id_contact = relationship('Users', foreign_keys = [id_contact])

    def __repr__(self):
        return '{}'.format(self.p_id_contact)


class Repository:

    def __init__(self):
        self.engine = create_engine(('sqlite:///server_db.db'))
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

    def update_users(self, username_old, username):
        pass

    def get_user(self, username):
        result = self.session.query(Users).filter_by(username = username).first()
        return result

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

if __name__ == '__main__':
    rep = Repository()
    # rep.logout('pilik')
    # print(rep.get_user('pilik').flag is False)
    # rep.add(UserContacts(1,3))
    # rep.add(Users('pilik5'))
    # print(rep.get_user('pilik5'))
    print(rep.get_user_contacts('pilik14'))
    for cont in rep.get_user_contacts('pilik14'):
        print(str(cont))