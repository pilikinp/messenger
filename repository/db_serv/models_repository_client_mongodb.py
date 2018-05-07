import pymongo


class Repository():

    def __init__(self, name):
        self.connect = pymongo.MongoClient
        self.db = self.connect['{}'.format(name)]


    def add_contact(self, name, publickey, avatar):
        col = self.db.contacts
        col.save({'name': name, 'publickey': publickey, 'avatar': avatar})

    def contacts_list(self):
        col = self.db.contacts
        return col.find()

    def get_contact(self, name):
        col = self.db.contacts
        return col.find({'name': name})

    def get_avatar(self):
        col = self.db.user
        return col.find()

    def get_avatar_contact(self, username):
        col = self.db.contacts
        return self.find({'name': username})['avatar']

    def add_histary(self, time, from_, to_, message):
        col = self.db.history
        col.save({'time':time, 'from': from_, 'to': to_, 'message': message})

    def get_history(self, name , username):
        col = self.db.history
        return col.find({'to': name})
        # найти как в mongodb осуществляется поиск по условию
        # return self.session.query(HistoryMessage).filter(((HistoryMessage.to_id == name) & (HistoryMessage.from_id == username)) | ((HistoryMessage.to_id == username) & (HistoryMessage.from_id == name))).all()

    def get_publickey(self,name):
        col = self.db.contacts
        return col.find({'name': name})['publickey']

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
