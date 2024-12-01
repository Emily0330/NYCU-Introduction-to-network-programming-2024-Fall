import socket
import threading
import time
from game1 import play_game1_client, play_game1_server
from game2 import play_game2_client, play_game2_server

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
invitation_list = [] # store [invitor, room id] 


lock = threading.Lock()
lock_reply = threading.Lock()
invitation_listener_stop = False
invitation_received = False
global_reply = 'not_yet_set'

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
        # print("The temporary server starts, waiting for others to invite.")
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
                    tmp_inv_list = invitation.split(' ')
                    invitation_list.append([tmp_inv_list[0],0]) # add host name, modify the room id! // TODO
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
        action = input("(R) Register\n(LI) Login\nPlease choose an action: ")
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
                # print("Do you want to create a room (C), join a public room (J), or log out (LO): ")
                print("(C) create a room\n(J) join a public room\n(LO) log out\n(IM) Go to Invitation Management\nPlease choose an action: ", end="")
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
                    
                    elif action == "IM":
                        my_state = 'in_invitaion_page'

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
        elif my_state == 'in_invitaion_page':
            print("Invitation Management\n(1) List all the requests\n(2) Accept a request\n(3) Back to lobby")
            action_in_inv_page = input()
            if action_in_inv_page == '1':
                
                print("You received invitations from the following rooms.")
                invitation_str = "    invitor    |   room id    \n"
                invitation_str += "---------------|---------------\n"
                for x in invitation_list:
                    invitation_str += f"{x[0]:<14} |   {x[1]:<13}\n"
                print(invitation_str)

            elif action_in_inv_page == '2':
                print("Please enter the room id of the room you want to join:")
                room_id = int(input())
                # TODO: transfer to server
            
            elif action_in_inv_page == '3':
                print("Going back to lobby...")
                my_state = 'idle'

