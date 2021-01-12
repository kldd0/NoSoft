#!/usr/bin/env python3
import socket
import threading
import time
import pyfiglet
import json
import db

db = db.DB()

def run(port=54321, max_connection=5):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port))
    server.listen()
    clients = []
    while True:
        sock, addr,clients = accept_conn(server, clients)
        t = threading.Thread(target=handle_client,
                             args=(sock, addr, clients))
        t.daemon = True
        t.start()
        #stop_threads = True
        #t.join() 
        if threading.active_count() > int(max_connection): exit(-1)


def accept_conn(server, clients):
    client_sock, client_addr = server.accept()
    clients.append(client_sock)
    print(f'\n#User successfully connected\n\
            With {client_sock}')
    return client_sock, client_addr,clients


def handle_client(sock, addr, clients):
    show_menu(sock)
    opt = sock.recv(1024).decode().strip('\n')
    if (opt == "1"):
        clear(sock)
        log = login(sock)
    elif (opt == "2"):
        clear(sock)
        log = register(sock)
    else:
        sock.sendall(b"\n\033[31m     This not an option! Choose valid number!\n")
        time.sleep(2)
        handle_client(sock,addr,clients)
    if not log: return 0
    main_page(sock,addr,log,clients)

    #while True:
     #   handle_message(sock, clients)


def show_menu(sock):
    clear(sock)
    s = '\x1b[8;22;106t'
    sock.sendall(s.encode())
    sock.sendall(b'''\033[32m 
      _   _      ____         __ _     __  __                                          
     | \ | | ___/ ___|  ___  / _| |_  |  \/  | ___  ___ ___  ___ _ __   __ _  ___ _ __ 
     |  \| |/ _ \___ \ / _ \| |_| __| | |\/| |/ _ \/ __/ __|/ _ \ '_ \ / _` |/ _ \ '__|
     | |\  | (_) |__) | (_) |  _| |_  | |  | |  __/\__ \__ \  __/ | | | (_| |  __/ |   
     |_| \_|\___/____/ \___/|_|  \__| |_|  |_|\___||___/___/\___|_| |_|\__, |\___|_|   
                                                                       |___/           \n''')

    sock.sendall(b'''      \033[32m NoSoft Messanger is the chat system that works on the invitations at the ID.\n          In settings.json you can change the port and load of the server.''')
    sock.sendall(b'''\n\n\n                             \033[32m Choose your login method:\n''')
    sock.sendall(b'''                                \033[32m (1) Login in account\n''')
    sock.sendall(b'''                                \033[32m (2) Register account\n''')
    sock.sendall(b'''\n\n    \033[32m  Enter 1 or 2 option: ''')
    sock.sendall(b'''\033[34m''')



def register(sock):
    sock.sendall(b''' \033[32m
      ____            _     _             _   _                                      
     |  _ \ ___  __ _(_)___| |_ _ __ __ _| |_(_) ___  _ __    
     | |_) / _ \/ _` | / __| __| '__/ _` | __| |/ _ \| '_ \  
     |  _ <  __/ (_| | \__ \ |_| | | (_| | |_| | (_) | | | | 
     |_| \_\___|\__, |_|___/\__|_|  \__,_|\__|_|\___/|_| |_| 
                |___/                                        \n
    ''')

    sock.sendall(b'\033[32mEnter your login: ')
    sock.sendall(b'''\033[34m''')
    login = sock.recv(1024).decode()
    if (db.exists_login(login)):
        sock.sendall(b'   \033[31m\n\nThis login already in use. Bye!\n')
        time.sleep(2)
        sock.close()

    else:
        sock.sendall(b'''    \033[32mEnter your pwd: ''')
        sock.sendall(b'''\033[34m''')
        pwd = sock.recv(1024).decode()
        db.add(login, pwd)
    
    db.insert_sock(login, sock)

    sock.sendall(b'''\n   \033[32m You have successfully registered!''')
    time.sleep(1)
    return login

def login(sock):
    sock.sendall(b'''\033[32m
      _                _                                
     | |    ___   __ _(_)_ __    _ __   __ _  __ _  ___ 
     | |   / _ \ / _` | | '_ \  | '_ \ / _` |/ _` |/ _ |
     | |__| (_) | (_| | | | | | | |_) | (_| | (_| |  __/
     |_____\___/ \__, |_|_| |_| | .__/ \__,_|\__, |\___|
                 |___/          |_|          |___/    \n\n''')
    sock.sendall(b'''   \033[32mEnter your login: ''')
    sock.sendall(b'''\033[34m''')
    login = sock.recv(1024).decode()
    sock.sendall(b'''   \033[32mEnter your pwd: ''')
    sock.sendall(b'''\033[34m''')
    pwd = sock.recv(1024).decode()
    if not (db.check(login, pwd)):
        sock.sendall(b'''\n   \033[31mIncorrect credentials. Bye!''')
        time.sleep(2)
        return False
    db.insert_sock(login, sock)
    return login

def clear(sock):
    s = '\033c'
    sock.sendall(s.encode())

def format_menu(sock):
    s = '\x1b[8;28;106t'
    sock.sendall(s.encode())


def main_page(sock,client,log,clients):
    clear(sock)
    s = '\x1b[8;33;90t'
    sock.sendall(s.encode())
    sock.sendall(b'''\033[32m
      __  __       _                                
     |  \/  | __ _(_)_ __    _ __   __ _  __ _  ___ 
     | |\/| |/ _` | | '_ \  | '_ \ / _` |/ _` |/ _ |
     | |  | | (_| | | | | | | |_) | (_| | (_| |  __/
     |_|  |_|\__,_|_|_| |_| | .__/ \__,_|\__, |\___|
                            |_|          |___/       \n\n''')
    s = f"Your address: {client[0]}:{client[1]}"
    sock.sendall(b'''   ''' + b"\033[32m" + s.encode() + b'\n')
    sock.sendall(b'''\033[32m
   There are 3 options to choose from:
       (1) View added rooms
       (2) Join a room
       (3) Create room\n\n''')
    sock.sendall(b'''   Select an option from the list: ''')
    sock.sendall(b'''\033[34m''')
    opt = sock.recv(1024).decode().strip('\n')
    if opt not in ["1","2","3"]:
        sock.sendall(b'''\033[31m\n   Choose valid 1,2 or 3 option!''')
        time.sleep(2)
        main_page(sock,client,log,clients)
    if (opt == "3"): create_room(sock,client,log,clients)
    if (opt == "2"): join_room(sock,client,log,clients)
    if (opt == "1"): show_list_of_rooms(sock,client,log,clients)

def create_room(sock,client,log,clients):
    clear(sock)
    sock.sendall(b''' \033[32m
       ____                _                                    
      / ___|_ __ ___  __ _| |_ ___    _ __ ___   ___  _ __ ___  
     | |   | '__/ _ \/ _` | __/ _ \  | '__/ _ \ / _ \| '_ ` _ \ 
     | |___| | |  __/ (_| | ||  __/  | | | (_) | (_) | | | | | |
      \____|_|  \___|\__,_|\__\___|  |_|  \___/ \___/|_| |_| |_|       
                                                           \n\n''')
    sock.sendall(b'''\033[32m     Create a name for the room:\033[34m ''')
    message = sock.recv(1024).decode().strip('\n\n')
    if db.exists_room_name(message):
        sock.sendall(b'''\033[31mThis name is already taken. Come up with another!''')
        create_room(sock)
        return False

    room_id = db.create_room(message,log)
    print(room_id)
    sock.sendall(b'''\n\n\033[32m     The room was added to the datadb. By this name you can find a room\n     from the list of rooms.\n     Others can use this ID to enter the room: \033[34m''' + str(room_id).encode())
    sock.sendall(b'''\n\n\033[32m     Press ENTER to continue...''')
    message = sock.recv(1024).decode().strip('\n\n')
    main_page(sock,client,log,clients)

def join_room(sock,client,log,clients):
    clear(sock)
    sock.sendall(b'''\033[32m
          _       _                                           
         | | ___ (_)_ __     _ __ ___   ___  _ __ ___  
      _  | |/ _ \| | '_ \   | '__/ _ \ / _ \| '_ ` _ \ 
     | |_| | (_) | | | | |  | | | (_) | (_) | | | | | |
      \___/ \___/|_|_| |_|  |_|  \___/ \___/|_| |_| |_|
                                                          \n
    ''')
    sock.sendall(b'''Enter the ID of the new room\n    from your saved ones:\033[34m ''')
    message = sock.recv(1024).decode().strip('\n\n')
    db.join_room_with_id(message, sock)
    if not NAME:
       sock.sendall(b'''\033[31mThe entered ID or name does not exist!''')
       join_room(sock,client,log)
       return False
    sock.sendall(b'''\n\n    \033[32mEntrance to the room...''')
    time.sleep(1)
    go_to_room(sock,NAME,messages,log,clients,client)

def go_to_room(sock,NAME,log,clients,client):
    clear(sock)
    ascii_banner = pyfiglet.figlet_format(NAME)
    sock.sendall(b'''\033[32m''' + ascii_banner.encode())

    sock.sendall(b'''\n \033[32m U can start chatting below. Type message!\n  (use :q! to exit on main page)\n\n''')
    while (handle_message(sock,clients,log,NAME)):
        clients = db.get_socks(NAME)

        handle_message(sock, clients, log,NAME)

    main_page(sock,client,log,clients)

def show_list_of_rooms(sock,client,log,clients):
    list_of_rooms, list_of_ids = db.display_personal_rooms(log)
    kol = 1
    sock.sendall(b'''\033[32m           -------------------------------------------------------------\n''')
    for room, id in zip(list_of_rooms,list_of_ids):
        sock.sendall(b'''               '''+ b'\033[32m(' + str(kol).encode() + b')' + b'''  ''' + b'Room name: ' +b'\033[34m' + room.encode() + b"\033[32m ---- "  + b"ID of room: " +b'\033[34m' +  id.encode() + b'\n\n')
        kol+=1
    sock.sendall(b'''\033[32m           -------------------------------------------------------------\n''')
    sock.sendall(b'''\033[32m\n    Enter the name of the room to connect to it:\033[34m ''')
    message = sock.recv(1024).decode().strip('\n\n')
    if message not in list_of_rooms:
        sock.sendall(b'''\033[31m\n    Incorrect name of room or the selected room is unavailable! ''')
        time.sleep(2)
        main_page(sock,client,log,clients)

    db.join_room(message, sock)
    go_to_room(sock,message,log,clients,client)


def handle_message(sock, clients,log,NAME):
    try:
        message = sock.recv(1024).decode().strip('\n\n')
        print(message)
        if message == ":q!": return False

        for el in clients:
            if el == sock:
                log = log.strip('\n\n')
                s = f'[\033[35m{log}\033[32m]: {message}\n'
            elif el != sock and message.strip(" ").strip('\n') != '':
                log = log.strip('\n\n')
                s = f'[\033[35m{log}\033[32m]: {message}\n'
            else:
                s = "Connection error!"
            if str(el)[0] == '<': el.sendall(s.encode())
            else: sock.sendto(s.encode(), el)
        return True
    except ConnectionResetError as e:
        print(e)


if __name__ == '__main__':
    print("The server starts working...\n")
    with open("settings.json","r") as settings:
        js  = json.loads(settings.read())
        port = js["port"]
        max_conn = js["max_connections"]
        print(f"Port: {port} and max_connections: {max_conn}")
        run(port,max_conn)