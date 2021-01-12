import sqlite3
import hashlib
import re
import os

class DB:
    def __init__(self):
        self.db_name = os.getcwd() + "/database.db"

    def add(self, login, password):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        login = hashlib.md5(login.encode()).hexdigest()
        password = hashlib.md5(password.encode()).hexdigest()
        cmd = f'''INSERT INTO creds(login, password) VALUES ('{login}', '{password}');'''
        cur.execute(cmd)
        conn.commit()
        conn.close()
        return True

    def check(self, login, password):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        login = hashlib.md5(login.encode()).hexdigest()
        password = hashlib.md5(password.encode()).hexdigest()
        cmd = f'''SELECT password FROM creds WHERE login='{login}';'''
        cur.execute(cmd)
        try:
            passwd_true = cur.fetchall()[0][0]
        except:
            conn.close()
            return False
        if password == passwd_true:
            conn.close()
            return True
        conn.close()
        return False

    def exists_login(self, login):

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        hash_login = hashlib.md5(login.encode()).hexdigest()
        cmd = f'''SELECT * FROM creds WHERE login='{hash_login}';'''
        cur.execute(cmd)
        if cur.fetchall() != []:
            conn.close()
            return True # логин уже используется
        conn.close()
        return False

    def room_id_by_name(self, name):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        regex = re.compile(r'^[a-zA-Z0-9]+([_!]{0,}?[a-zA-Z0-9]+){0,2}$')
        check = re.match(regex, name)
        try:
            text = check.group()
            if name != text:
                conn.close()
                return False # недопустимое имя
        except:
            conn.close()
            return False # недопустимое имя
        cmd = f'''SELECT room_id FROM rooms WHERE room_name='{name}';'''
        cur.execute(cmd)
        try:
            id = cur.fetchall()[0][0]
        except:
            conn.close()
            return False # не существует комнаты с этим именем
        conn.close()
        return id

    def create_room(self, name, owner,sock):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        regex = re.compile(r'^[a-zA-Z0-9]+([_!]{0,}?[a-zA-Z0-9]+){0,2}$')
        check = re.match(regex, name)
        try:
            text = check.group()
            if name != text:
                conn.close()
                return False
        except:
            conn.close()
            return False # недопустимое имя
        sock = str(sock).replace("'",'#')
        id = sum(list(map(lambda x: int('0b'+x, 2), ' '.join(format(ord(x), 'b') for x in name).split()))) # принцип присваивания id
        cmd = f'''INSERT INTO rooms(room_name, room_id, sockets) VALUES('{name}', '{id}', '{sock}');''' # -1 так как пока хз, для чего это
        cur.execute(cmd)
        conn.commit()
        hash_login = hashlib.md5(owner.encode()).hexdigest()
        cmd = f'''SELECT * FROM creds WHERE login='{hash_login}';'''
        cur.execute(cmd)
        res = cur.fetchall()
        pwd, rooms, sock = res[0][1], res[0][2], res[0][3]
        cmd = f'''INSERT INTO creds(login, password, names_of_rooms, socket) VALUES ('{hash_login}','{pwd}','{rooms + "," + name if rooms != None else name}', '{sock}');'''
        cur.execute(cmd)
        conn.commit()
        conn.close()  
        return id

    def exists_room_name(self, name):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        regex = re.compile(r'^[a-zA-Z0-9]+([_!]{0,}?[a-zA-Z0-9]+){0,2}$')
        check = re.match(regex, name)
        try:
            text = check.group()
            if name != text:
                conn.close()
                return False
        except:
            conn.close()
            return False
        cmd = f'''SELECT * FROM rooms WHERE room_name='{name}';'''
        cur.execute(cmd)
        if cur.fetchall() != ():
            conn.close()
            return False
        conn.close()
        return True

    def display_personal_rooms(self,name):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        hash_login = hashlib.md5(name.encode()).hexdigest()
        cmd = f'''SELECT names_of_rooms FROM creds WHERE login='{hash_login}';'''
        cur.execute(cmd)
        res = cur.fetchall()[0]
        
        if res[0] == 'None':
            conn.close()
            return [], []
        ids = []
        res = res[0].split(',')
        for el in res:
            cmd = f'''SELECT room_id FROM rooms WHERE room_name='{el}';'''
            cur.execute(cmd)
            ids.append(cur.fetchall()[0][0])
        return res, ids
    
    def insert_sock(self,login,sock):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        hash_login = hashlib.md5(login.encode()).hexdigest()
        cmd = f'''SELECT * FROM creds WHERE login='{hash_login}';'''
        cur.execute(cmd)
        res = cur.fetchall()
        sock = str(sock).replace("'",'#')
        pwd, rooms, _ = res[0][1], res[0][2], res[0][3]
        cmd = f'''INSERT INTO creds(login, password, names_of_rooms, socket) VALUES ('{hash_login}','{pwd}','{rooms}', '{sock}');'''
        cur.execute(cmd)
        conn.commit()
        conn.close()
        return True

    def join_room(self, name, sock):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cmd = f'''SELECT * FROM rooms WHERE room_name='{name.strip()}';'''
        cur.execute(cmd)
        res = cur.fetchall()[0]
        room_id, sockets = res[1], res[2]
        sock = str(sock).replace("'",'#')
        cmd = f'''INSERT INTO rooms(room_name, room_id, sockets) VALUES ('{name.strip()}','{room_id}','{sockets + ',' + sock if sockets != None else sock}');'''
        cur.execute(cmd)
        conn.commit()
        conn.close()
        return

    def get_socks(self,name):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cmd = f'''SELECT * FROM rooms WHERE room_name='{name.strip()}';'''
        cur.execute(cmd)
        res = cur.fetchall()[0][0]
        if res == None:
            conn.close()
            return False
        send = []
        for el in res:

            sends = el.replace('#',"'")[124:-2].split(',')
            send.append((sends[0].replace("'",''), int(sends[1].strip())))
        conn.close()
        return send

    def join_room_with_id(self,id,sock):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cmd = f'''SELECT * FROM rooms WHERE room_id='{str(id).strip()}';'''
        cur.execute(cmd)
        res = cur.fetchall()[0]

        if res[0] == None: return False
        room_name, sockets = res[0], res[2]
        sock = str(sock).replace("'",'#')
        cmd = f'''INSERT INTO rooms(room_name, room_id, sockets) VALUES ('{room_name}','{id}','{sockets + ',' + sock if sockets != None else sock}');'''
        cur.execute(cmd)
        conn.commit()
        conn.close()
        return room_name