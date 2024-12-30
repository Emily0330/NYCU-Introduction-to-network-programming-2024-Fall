import socket
import threading
import time

MY_IP = '0.0.0.0'
MY_PORT = int(input("Please enter which port you want to set the server on: "))

# server_ip = input("Please enter the game server IP you want to connect to: ")
# server_port = int(input("Please enter the game server port: "))
server_ip = '140.113.235.152'
server_port = 40169

connected = False
loggedin = False
start_game = False
joining_public_room = False
join_room_game_type = 'not_yet_set' # remember to reset these value
my_state = 'idle'
my_username = 'not_yet_set_name' # remember to reset once log out
my_pwd = 'not_yet_set_pwd' # remember to reset once log out
my_room = ['no_room', MY_IP, MY_PORT, 'no_game'] # 'public/private/no_room', room_ip, room_port, game1

lock = threading.Lock()
lock_reply = threading.Lock()
invitation_listener_stop = False
invitation_received = False
global_reply = 'not_yet_set'

def print_graph_game1(choice):
    if(choice == '3'):
        print("""⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⢀⣤⡤⠦⢤⡀⠄⠄⠄⢀⣤⡴⠦⣤⡀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⢰⡟⠁⠄⠄⠄⠙⣆⠄⣰⠟⠁⠄⠄⠄⠹⡆⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⢸⡇⠄⠄⠄⠄⠄⢹⣦⡟⠄⠄⠄⠄⠄⠄⡇⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠘⣇⠄⠄⠄⠄⠄⠈⣿⡇⠄⠄⢀⣠⣤⣼⣇⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⢹⡄⠄⠄⠄⣀⣀⣿⠄⠄⣴⠛⠁⠄⠄⠙⣧⠤⣤⡀⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⢀⣽⠶⠛⠋⠉⠉⠙⠛⠻⣧⠄⠄⠄⠄⠄⢸⡇⠄⢻⡄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⣠⠟⠁⠄⠄⠄⠄⠄⠄⠄⠄⣸⠆⠄⠄⠄⠄⣼⠃⠄⢸⡇⠄⠄⠄⠄
⠄⠄⠄⠄⠄⢠⡏⠄⠄⠄⠄⠄⣀⣀⣠⡤⠞⢿⣄⣀⣀⣤⠾⠃⠄⢀⣼⠃⠄⠄⠄⠄
⠄⠄⠄⠄⠄⢸⡇⠄⠄⠄⠄⠈⢻⡍⠄⠄⠄⠄⠈⠉⠉⠙⠛⠖⠛⠉⣾⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⢿⡄⠄⠄⠄⠄⠄⠿⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢠⡟⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠻⣆⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⣠⠟⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⢹⡷⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠘⠛⣧⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠘⢧⣄⣀⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⣀⣤⠟⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⠉⠙⠛⠛⠛⠛⠛⠛⠛⠛⠉⠉⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
""")
    elif(choice == '2'):
        print("""⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⣀⣤⣀⡀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣰⡟⠉⠉⠉⠻⣆⠄⣴⡶⠶⠶⣤⡀⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⢠⡴⠖⠲⢦⣄⡟⠄⠄⠄⠄⠄⢻⣼⠁⠄⠄⠄⠈⣷⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⡟⠄⠄⠄⠄⠹⣷⠄⠄⠄⠄⠄⢸⡇⠄⠄⠄⠄⠄⣿⢀⣀⣀⡀⠄⠄⠄
⠄⠄⠄⠄⠄⣷⠄⠄⠄⠄⠄⢹⣧⠄⠄⠄⠄⢸⡇⠄⠄⠄⠄⢰⡿⠋⠁⠉⠹⡆⠄⠄
⠄⠄⠄⠄⢀⣸⣧⣤⣄⡀⠄⠄⢻⣄⣀⣤⣤⣼⣇⣀⡀⠄⣠⡟⠁⠄⠄⠄⢠⡇⠄⠄
⠄⠄⠄⢰⡟⠁⠄⠄⠈⠙⢷⡒⠛⠉⠁⠄⠄⠄⠄⠉⠉⠛⠯⠄⠄⠄⣠⡴⠏⠄⠄⠄
⠄⠄⠄⠸⢧⡀⠄⠄⠄⠄⠈⢷⡄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢰⡟⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠈⠙⣦⠄⠄⠄⠄⠈⠹⣆⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢸⠇⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠘⣇⠄⠄⠄⠄⠄⠛⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⡾⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠙⢷⣄⡀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⣤⠞⠁⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⣹⠃⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠛⢻⡆⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠘⠳⢤⣤⣄⣀⣀⣀⣀⣀⣀⣠⣤⠴⠛⠁⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠉⠉⠉⠉⠉⠉⠉⠉⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
""")
    else: # choice == '1'
        print("""⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⣤⣤⣄⡀⢀⣀⣀⡀⠄⠄⣀⣀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⣠⠟⠋⠁⠄⠈⠻⣏⠉⠉⠙⢳⡟⠉⠉⠛⣦⠶⠶⣤⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⢀⣯⠶⠛⠛⠳⣆⠄⢸⡇⠄⠄⠄⢹⡆⠄⠄⠘⣷⠄⠄⢿⡆⠄⠄⠄
⠄⠄⠄⠄⠄⣴⠛⠄⠄⠄⠄⠄⢸⠇⢠⡇⠄⠄⠄⢸⣿⠄⠄⠄⣿⠄⠄⠈⡧⠄⠄⠄
⠄⠄⠄⠄⢰⠏⠄⠄⠄⠄⣀⡶⠏⢀⡼⠃⠄⠄⢀⡼⠁⠄⠄⣠⠏⠄⠄⣴⠇⠄⠄⠄
⠄⠄⠄⠄⢸⡀⠄⠄⠄⠄⠈⠙⢷⡿⠷⢦⠴⠶⠻⠷⠴⠶⠾⠷⠶⠶⠛⣿⠆⠄⠄⠄
⠄⠄⠄⠄⠈⣷⠄⠄⠄⠄⠄⠄⠄⢻⡀⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⡿⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠈⢷⣀⠄⠄⠄⠄⠄⠈⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢀⡾⠁⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠛⣶⣤⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣠⣤⠛⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⣿⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⣷⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠛⠶⣤⣤⣄⣀⣀⣀⣀⣀⣀⣀⣀⣠⣤⡤⠛⠁⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠉⠉⠉⠉⠉⠉⠉⠁⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
""")

def play_game1_server(skt):
    client_choice = skt.recv(1024).decode('ascii')
    if len(client_choice) == 0: 
        print("Client closed the connection")
        return
    choice = input("Please enter your choice (1:rock/2:paper/3:scissors): ")
    print_graph_game1(choice)
    # skt.send(choice.encode())
    if client_choice == choice:
        print("Tie")
        client_msg = "Tie"
    elif client_choice == '1':
        if choice == '2':
            print("You win!")
            client_msg = "You lose QAQ"
        else:
            print("You lose QAQ")
            client_msg = "You win!"
    elif client_choice == '2':
        if choice == '1':
            print("You lose QAQ")
            client_msg = "You win!"
        else:
            print("You win!")
            client_msg = "You lose QAQ"
    else: # client_choice == '3':
        if choice == '1':
            print("You win!")
            client_msg = "You lose QAQ"
        else:
            print("You lose QAQ")
            client_msg = "You win!"

    skt.send(client_msg.encode())

def play_game1_client(skt):
    choice = input("Please enter your choice (1:rock/2:paper/3:scissors): ")
    print_graph_game1(choice)
    skt.send(choice.encode())
    print("Waiting for server's response...")
    result = skt.recv(1024).decode('ascii')
    if len(result) == 0:
        print("Connection broken.")
        return
    print(result)

def calculate_bulls_and_cows(secret, guess):
    """計算幾A幾B"""
    # bulls = sum(1 for s, g in zip(secret, guess) if s == g)
    bulls = 0
    for i in range(4):
        if secret[i] == guess[i]:
            bulls += 1
    cows = 0
    for i in range(4):
        if guess[i] in secret and guess[i] != secret[i]:
            cows += 1 
    return bulls, cows

def play_game2_client(skt):
    # print("I am game2 client!")
    """客戶端邏輯"""
    client_secret = input("Please enter your secret number (4 different digits): ")
    client_attempts, server_attempts = 0, 0
    # msg = skt.recv(1024).decode('ascii')
    while True:
        # 客戶端的猜測
        client_guess = input("Please enter your guess (4 different digits): ")
        skt.send(client_guess.encode())
        client_attempts += 1

        # 接收伺服器的回應
        server_response = skt.recv(1024).decode()
        if len(server_response) == 0:
            print("Another player disconnects.")
            return
        print(f"server replies: {server_response}")

        if server_response == "win":
            print("You win!")
            break
        else:
            skt.send(b"your_turn")
            # 接收伺服器的猜測
            server_guess = skt.recv(1024).decode()
            if len(server_guess) == 0:
                print("Another player disconnects.")
                return
            print(f"Receive server guess: {server_guess}")

            # 計算伺服器的猜測結果
            server_attempts += 1
            bulls, cows = calculate_bulls_and_cows(client_secret, server_guess)
            response = f"{bulls}A{cows}B"
            skt.send(response.encode())

            if bulls == 4:
                print(f"You lose. Server guess counts: {server_attempts}")
                break

def play_game2_server(skt):
    # print("I am game2 server!")
    """伺服器邏輯"""
    server_secret = input("Please enter your secret number (4 different digits): ")
    server_attempts, client_attempts = 0, 0

    while True:
        # 接收客戶端的猜測
        client_guess = skt.recv(1024).decode()
        if len(client_guess) == 0:
            print("Another player disconnects.")
            return
        client_attempts += 1
        bulls, cows = calculate_bulls_and_cows(server_secret, client_guess)
        client_response = f"{bulls}A{cows}B"
        if client_response == "4A0B":
            skt.send(b"win")
            print(f"client wins! Guess counts: {client_attempts}")
            break
        else:
            skt.send(client_response.encode())
            print(f"client's guess: {client_guess}, reply: {client_response}")
            _ = skt.recv(1024).decode() # my turn msg
            if len(_) == 0:
                print("Another player disconnects.")
                return
            # 伺服器的猜測
            server_guess = input("Please enter your guess (4 different digits): ")
            skt.send(server_guess.encode())
            server_attempts += 1

            # 接收客戶端的回應
            server_response = skt.recv(1024).decode()
            if len(server_response) == 0:
                print("Another player disconnects.")
                return
            print(f"Your guess: {server_guess}, client reply: {server_response}")

            if "4A0B" in server_response:
                print(f"You win! Guess counts: {server_attempts}")
                # skt.send(b"win")
                break

def build_connection(my_ip, my_port, player_ip, player_port):
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    skt.bind((my_ip,my_port))
    skt.connect((player_ip,player_port))
    connected = True
    return skt, connected

accept_invitation = False
def invitation_listener():
    global my_state, start_game, lock, invitation_listener_stop, invitation_received, lock_reply, accept_invitation, global_reply
    # print("The invitation listener starts!") # test
    tmp_server_start = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # accept_invitation = False
    game_ip = 'not_yet_known_ip' # declared here due to scope problem
    game_port = 'not_yet_known_port'
    try:
        s.bind((MY_IP, MY_PORT + 2)) # do i have to bind?
        s.listen(1) # allow game server to connect
        tmp_server_start = True
        print("The temporary server starts, waiting for others to invite.")
    except:
        print("Some error occurred when starting the temporary server.")
    if tmp_server_start:
        while True:
            new_skt, addr = s.accept()
            # lock.acquire()
            if my_state == 'idle' : # and not invitation_listener_stop
                # lock.release()
                if not accept_invitation:
                    print(f"Connected with game server at ip {addr[0]}, port {addr[1]}")
                    invitation = new_skt.recv(1024).decode('ascii')
                    print(invitation)
                    # print("acquiring lock by listener...") # test
                    lock.acquire()
                    # print("lock aquired!") # test
                    # print("acquiring lock_reply...") # test
                    lock_reply.acquire()
                    # print("lock_reply aquired!") # test
                    if global_reply == 'not_yet_set':
                        join_or_not = input()
                    elif global_reply == 'Y' or global_reply == 'N':
                        join_or_not = global_reply
                    else: # 'C' or 'LO' or 'J'
                        lock_reply.release()
                        # print("lock_reply released by listener.")
                        lock.release()
                        # print("lock released by listener.")
                        new_skt.close()
                        continue
                    lock_reply.release()
                    # print("lock_reply released by listener.")
                    
                    new_skt.send(join_or_not.encode())
                    if join_or_not == 'Y':
                        accept_invitation = True
                        print("Waiting for room information...")
                    else: # do not want to join the room
                        global_reply = 'not_yet_set' # newly added
                        print("Invitation rejected.")
                        lock.release()
                        # print("lock released by listener")
                        continue
                        # break
                    
                    new_skt.close()
                else: # has accepted the invitation or wanted to join public room  # get room information from game server
                    print(f"Connected with lobby server at ip {addr[0]}, port {addr[1]}")
                    game_ip = new_skt.recv(1024).decode('ascii')
                    new_skt.send(b"game ip received")
                    game_port = int(new_skt.recv(1024).decode('ascii'))
                    print(f"Receive game server's ip {game_ip} and port {game_port}, ready to connect...")
                    new_skt.send(b"game port received.")
                    join_room_game_type = new_skt.recv(1024).decode('ascii')
                    # print(f"join_room_game_type: {join_room_game_type}") # test
                    new_skt.send(b"game type received.")
                    new_skt.close()

                    start_game = True
                    my_state = 'in_game'
                    
                    if start_game:
                        try:
                            skt, connected = build_connection(MY_IP,MY_PORT,game_ip,game_port)
                        except Exception as e:
                            print("Failed to connect to game room server.")
                            print(e)
                        if connected:
                            global_reply = 'not_yet_set' # newly added
                            if join_room_game_type == 'game1':
                                play_game1_client(skt)
                            else: # game2
                                play_game2_client(skt)
                    
                    lock.release()
                    # print("lock released by listener")
                    continue
            else:
                lock.release()
                new_skt.close()
        
# main function starts

invitation_listener_thread = threading.Thread(target = invitation_listener)
invitation_listener_thread.start()
lock_by_main = False
while True:
    # print(my_state)
    if not loggedin:
        global_reply = 'not_yet_set'
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((MY_IP,MY_PORT))
            s.connect((server_ip,server_port))
            connected = True
        except Exception as e:
            print(e)
            print("Cannot connect to server.")
            time.sleep(3)

        if connected:
            action = input("Register(R) or Login(LI): ")
            first_time = True
            while True:
                s.send(action.encode())
                # print("sent action:",action) # test
                # print(first) # test
                if first_time:
                    username_prompt = s.recv(1024).decode('ascii')
                    username = input(username_prompt)
                    first_time = False
                s.send(username.encode())
                # print("sent usrname:",username) # test
                reply = s.recv(1024).decode('ascii')
                if "password" in reply: # username OK
                    pwd = input(reply)
                    s.send(pwd.encode())
                    # print("sent pwd:",pwd) # test
                    reply = s.recv(1024).decode('ascii')
                    
                    if reply == "Incorrect password.":
                        print(reply)
                        continue
                    elif reply == "Registration succeeds! Please type LI to login: ":
                        action = input(reply)
                        first_time = True
                        continue
                    else: # log in successfully?!
                        loggedin = True
                        my_username = username
                        my_pwd = pwd
                        my_state = 'idle'
                        print(reply)
                        
                        online_status = s.recv(1024).decode('ascii')
                        print(online_status) # room list
                        online_status = s.recv(1024).decode('ascii')
                        print(online_status) # player list
                        break
                else:
                    if action == 'R': # registration fails
                        username = input(reply)
                    else: # login fails
                        action = input(reply)
            s.close()
            connected = False
    else: # logged in, show rooms or create room
        if my_state == 'idle':
            if lock_by_main:
                lock.release()
                lock_by_main = False
                # print("lock released by main!")
            # lock2.acquire()
            # print(f"global_reply: {global_reply}") # test
            if not joining_public_room and global_reply != 'Y' and global_reply != 'N':# and not invitation_received
                # print("acquiring lock by main...")
                lock.acquire()
                lock_by_main = True
                # print("lock aquired by main!") # test
                # print(f"my_state: {my_state}")
                # print("acquiring lock_reply by main...")
                lock_reply.acquire()
                # print("lock_reply acquired by main!")
                # print("global reply released by main")
                global_reply = 'not_yet_set'
                
                if my_state == 'in_game':
                    lock_reply.release()
                    # print("lock_reply released by main")
                    lock.release()
                    lock_by_main = False
                    # print("lock released by main")
                    
                    continue
                
                # print("prompt1: choose your action: ")
                print("Do you want to create a room (C), join a public room (J), or log out (LO): ")
                # print("acquiring lock_reply by main...")
                # lock_reply.acquire()
                # print("lock_reply acquired by main!")
                # print(f"global reply: {global_reply}") # test
                if global_reply == 'not_yet_set':
                    global_reply = input()
                    action = global_reply
                elif global_reply == 'Y' or global_reply == 'N':
                    lock_reply.release()
                    # print("lock_reply released by main")
                    lock.release()
                    lock_by_main = False
                    # print("lock released by main")
                    continue
                else:
                    action = global_reply
                
                if global_reply == 'Y' or global_reply == 'N':
                    lock_reply.release()
                    # print("lock_reply released by main")
                    lock.release()
                    lock_by_main = False
                    # print("lock released by main")
                    continue
                # print(f"global reply: {global_reply}")
                
                lock_reply.release()
                # print("lock_reply released by main")

                # if action == 'C' or action == 'J' or action == 'LO':
                # lock.acquire()
                invitation_listener_stop = True
                # lock.release()
            # if invitation_listener_stop: # W 也要在這下面嗎?
            tmp_server_start = False
            if action == 'W' or joining_public_room: # waitng to join
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # test do i need
                accept_invitation = False
                game_ip = 'not_yet_known_ip' # declared here due to scope problem
                game_port = 'not_yet_known_port'
                try:
                    s.bind((MY_IP, MY_PORT)) # do i have to bind?
                    s.listen(1) # allow game server to connect
                    tmp_server_start = True
                    if joining_public_room:
                        print("The temporary server starts, waiting for room information.")
                    else:    
                        print("The temporary server starts, waiting for others to invite.")
                except:
                    print("Some error occurred when starting the temporary server.")
                
                if tmp_server_start:
                    while True:
                        new_skt, addr = s.accept()
                        if not accept_invitation and not joining_public_room:
                            print(f"Connected with game server at ip {addr[0]}, port {addr[1]}")
                            invitation = new_skt.recv(1024).decode('ascii')
                            join_or_not = input(invitation)
                            new_skt.send(join_or_not.encode())
                            if join_or_not == 'Y':
                                accept_invitation = True
                                print("Waiting for room information...")
                            else: # do not want to join the room
                                print("Invitation rejected.")
                                break
                            
                            new_skt.close()
                        else: # has accepted the invitation or wanted to join public room  # get room information from game server
                            print(f"Connected with game server at ip {addr[0]}, port {addr[1]}")
                            game_ip = new_skt.recv(1024).decode('ascii')
                            okay = "game ip received"
                            new_skt.send(okay.encode())
                            game_port = int(new_skt.recv(1024).decode('ascii'))
                            print(f"Receive game server's ip {game_ip} and port {game_port}, ready to connect...")
                            new_skt.send(b"game port received.")
                            join_room_game_type = new_skt.recv(1024).decode('ascii')
                            # print(f"join_room_game_type: {join_room_game_type}") # test
                            new_skt.send(b"game type received.")
                            new_skt.close()
                            s.close()
                            time.sleep(5)
                            tmp_server_start = False
                            start_game = True
                            my_state = 'in_game'
                            break
                    if start_game:
                        try:
                            skt, connected = build_connection(MY_IP,MY_PORT,game_ip,game_port)
                        except Exception as e:
                            print("Failed to connect to game room server.")
                            print(e)
                        if connected:
                            if join_room_game_type == 'game1':
                                play_game1_client(skt)
                            else: # game2
                                play_game2_client(skt)
                            
                            skt.close()
                            time.sleep(5)
                            my_state = 'idle'
                            join_room_game_type = 'not_yet_set' # reset join_room_game_type
                            start_game = False
                            joining_public_room = False
                            # break
            elif global_reply != 'Y' and global_reply != 'N':
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((MY_IP,MY_PORT))
                    s.connect((server_ip,server_port)) # to change an address
                    connected = True
                except:
                    print("Cannot connect to server. Please try again later.")
                
                joining_public_room = False # to control the socket close
                if connected:
                    s.send(action.encode())
                    # print(f"action {action} sent to lobby.") # test
                    if action == 'C':
                        reply = s.recv(1024).decode('ascii')
                        pub_or_pri = input(reply)
                        s.send(pub_or_pri.encode())
                        reply = s.recv(1024).decode('ascii')
                        game = input(reply)
                        s.send(game.encode())
                        reply = s.recv(1024).decode('ascii') # ask for username msg
                        s.send(my_username.encode())
                        reply = s.recv(1024).decode('ascii')# room creation success msg
                        my_state = 'in_room' # change player state to in room
                        my_room[0] = 'public' if pub_or_pri == '1' else 'private'
                        my_room[3] = 'game1' if game == '1' else 'game2'
                        print(reply) # room creation success msg
                    elif action == 'J': # action == 'J'
                        # print("I am going to join a public room!")
                        reply = s.recv(1024).decode('ascii')
                        if reply == 'No public game rooms available':
                            print(reply)
                            lock.release()
                            lock_by_main = False
                            continue
                        
                        while True:
                            public_room_id = input(reply) # ask which public room
                            s.send(public_room_id.encode())
                            reply = s.recv(1024).decode('ascii')
                            if 'room is full' in reply:
                                print(reply)
                            else:
                                break
                        
                        # get room information
                        join_room_game_type = reply
                        # print(f"join_room_game_type: {join_room_game_type}") # test
                        joining_public_room = True
                        s.send(my_username.encode())

                    elif action == 'LO': # action == 'LO'
                        print("going to log out...")
                        loggedin = False
                        _ = s.recv(1024).decode('ascii') # asked for username
                        s.send(my_username.encode())
                        log_out_msg = s.recv(1024).decode('ascii')
                        print(log_out_msg)

                # lock.release()
                # print("lock released by main")

                # if not joining_public_room:
                s.close()
                connected = False
                time.sleep(1) # 不讓他太快下個iteration，讓socket好好關閉
            # lock.acquire()
            # invitation_stop = False
            # lock.release()
        elif my_state == 'in_room':
            if my_room[0] == 'public':
                tmp_server_start = False
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((MY_IP,MY_PORT + 1))
                    s.listen(1) # allow game server to connect
                    tmp_server_start = True
                    print("The temporary server starts, waiting for response.")
                except Exception as e:
                    print(e)
                    print("Cannot connect to server. Please try again later.")
                
                if tmp_server_start:
                    # print("Waiting for another player to join...")
                    new_skt, addr = s.accept()
                    print(f"Connected with lobby at ip {addr[0]}, port {addr[1]}")
                    # start deliver ip & port of the room to lobby
                    player_found_msg = new_skt.recv(1024).decode('ascii')
                    print(player_found_msg, "Setting up the room server...")
                    
                    my_room[1] = MY_IP
                    my_room[2] = MY_PORT + 1
                    new_skt.close() # end the connection with the lobby server

                    print("Waiting another player to connect...")
                    game_skt, player_addr = s.accept()
                    
                    print("Connected! Starting the game...")
                    my_state = 'in_game'
                    if my_room[3] == 'game1':
                        play_game1_server(game_skt)
                        game_skt.close()
                        # s will close below

                    else: # game2
                        play_game2_server(game_skt)
                        game_skt.close()


            else: # private room
                action = input("Type I to see who you can invite, you can only invite idle player.")
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((MY_IP,MY_PORT))
                    s.connect((server_ip,server_port)) # to change an address
                    connected = True
                except:
                    print("Cannot connect to server. Please try again later.")
                
                if connected:
                    s.send(action.encode())
                    player_str = s.recv(1024).decode('ascii')
                    print(player_str)
                    # person_to_invite = input("Please enter the idle player you want to invite: ")
                    while True:
                        person_to_invite = input("Please enter the idle player you want to invite: ")
                        s.send(person_to_invite.encode())
                        okay = s.recv(1024).decode('ascii') # receive okay msg
                        if 'okay' in okay:
                            break
                        else:
                            print(okay)
                    # s.recv(1024).decode('ascii') # receive okay msg
                    s.send(my_username.encode())
                    
                    s.close()
                    connected = False
                    time.sleep(3) # 讓s好好關閉

                    print("Waiting for response...")
                    tmp_server_start = False
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    try:
                        print(MY_IP, MY_PORT)
                        s.bind((MY_IP, MY_PORT + 1)) # do i have to bind?
                        s.listen(1) # allow game server to connect
                        tmp_server_start = True
                        print("The temporary server starts, waiting for response.")
                    except:
                        print("Some error occurred when starting the temporary server.")
                    
                    if tmp_server_start: # waiting for server's connection
                        new_skt, addr = s.accept()
                        print(f"Connected with lobby at ip {addr[0]}, port {addr[1]}")
                        accepted = new_skt.recv(1024).decode('ascii')
                        if accepted == 'Y':
                            # go to set up the room server
                            print("going to set up the room server!")
                            my_room[1] = MY_IP
                            my_room[2] = MY_PORT + 1
                            new_skt.close() # end the connection with the lobby server

                            print("Waiting another player to connect...")
                            game_skt, player_addr = s.accept() # wait for another client to connect
                            print("Connected! Starting the game...")
                            my_state = 'in_game'
                            if my_room[3] == 'game1':
                                play_game1_server(game_skt)
                                game_skt.close()
                                # s will close below

                            else: # game2
                                play_game2_server(game_skt)
                                game_skt.close()

                        else: # invitation rejected
                            print("Invitation rejected.")
                            new_skt.close()
                            s.close()
                            connected = False
                            tmp_server_start = False
                            time.sleep(5)
                        
            if action != 'I': # have closed the socket in I       
                s.close()
                connected = False
                time.sleep(5)
        elif my_state == 'in_game': # game server Notifies the End of the game (自己它的state，只有client自己有這個state，在lobby還是in_room)
            action = 'NE' #Notify End of the game to lobby server
            my_state = 'idle'
            my_room[0] = 'no_room' # the room dissolves
            lock_reply.acquire()
            global_reply = 'not_yet_set'
            lock_reply.release()
            try:
                skt, connected = build_connection(MY_IP, MY_PORT, server_ip, server_port)
            except Exception as e:
                print("Cannot connect to lobby server.")
                print(e)
            if connected:
                skt.send(action.encode())
                _ = skt.recv(1024).decode('ascii')
                skt.send(my_username.encode())
                
                skt.close()
                time.sleep(3) # change this from 5 to 3, see if it's ok
