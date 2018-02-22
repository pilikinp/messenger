from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []
print('ведите сколько клиентов запустить')
while True:
    user = input()
    if user == 'q':
        break
    for i in range(int(user)):
        p_list.append(Popen('python test.py', creationflags= CREATE_NEW_CONSOLE))
