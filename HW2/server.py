import socket
import time

# linux_server = input("Which linux server are you on? (1, 2, 3, or 4): ")
# MY_IP = f"140.113.235.15{linux_server}"
MY_IP = f"140.113.235.152"
MY_PORT = 40169

user_dict = {} # username:[pwd,state,ip,port]
room_dict = {} # room_idx:['private','roomhost','waiting/ingame/dissolve', 'game1/game2', 'another person']

room_idx = 0

def build_connection(my_ip, my_port, player_ip, player_port):
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    skt.bind((my_ip,my_port))
    skt.connect((player_ip,player_port))
    connected = True
    return skt, connected

server_start = False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((MY_IP, MY_PORT)) # do i have to bind?
    s.listen(5) # the max size of waiting queue of connection is 5
    server_start = True
    print("The game server starts, waiting for players to connect.")
except Exception as e:
    print(e)
    print("Some error occurred when starting the server.")

if server_start:
    
    while True:
        new_skt, addr = s.accept()
        print(f"Connected with client at ip {addr[0]}, port {addr[1]}")
        first_time = True
        username = 'not_yet_set'
        name_exist = True # initialized here due to scope
        while True:
            action = new_skt.recv(1024).decode('ascii')

            # print(f"action: {action}") # test
            if action == 'R' or action == 'LI':
                if first_time:
                    prompt1 = "Please enter your username: "
                    new_skt.send(prompt1.encode())
                    first_time = False
                
                username = new_skt.recv(1024).decode('ascii')
                name_exist = (username in user_dict)

                if (action == 'LI' and name_exist) or (action == 'R' and not name_exist):
                    new_skt.send(b"Please enter your password: ")
                    pwd = new_skt.recv(1024).decode('ascii')
                    
                    if action == 'R':
                        user_dict[username] = [pwd, 'idle', 'init_ip', -1] # add username & pwd to dict
                        first_time = True
                        new_skt.send(b"Registration succeeds! Please type LI to login: ")
                        # break
                    else:
                        if pwd == user_dict[username][0]:
                            logged_in = "Login succeeds!" 
                            new_skt.send(logged_in.encode())
                            user_dict[username][1] = 'idle'
                            user_dict[username][2] = addr[0] # player ip
                            user_dict[username][3] = addr[1] # player port
                            # display online status
                            table_str = "\nroom_idx | private/public | roomhost | status    | game\n"
                            table_str += "----------------------------------------------------\n"
                            for idx, values in room_dict.items():
                                if values[2] != 'dissolve':
                                    table_str += f"{idx:<8} | {values[0]:<14} | {values[1]:<8} | {values[2]:<9} | {values[3]}\n"
                            
                            new_skt.send(table_str.encode())

                            player_str = "\n     username     |  state  \n"
                            player_str += "-----------------------------\n"
                            for idx, values in user_dict.items():
                                if values[1] != "log_out":
                                    player_str += f"{idx:<17} | {values[1]}\n"
                            new_skt.send(player_str.encode())
                            break
                        else: # wrong pwd
                            new_skt.send(b"Incorrect password.")  
                else: 
                    if action == 'R': # invalid username
                        new_skt.send(b"Username already exists. Please enter another username: ")
                    else: # not yet registered
                        new_skt.send(b"You are not registered. Please type R to register: ")
            elif action == 'C':
                new_skt.send(b"Do you want a public room (1) or a private one (2): ")
                reply = new_skt.recv(1024).decode('ascii')
                pub_or_pri = 'public' if reply == '1' else 'private' 
                prompt4 = f"which game do you want? game1 (1) or game2 (2): "
                new_skt.send(prompt4.encode())
                reply = new_skt.recv(1024).decode('ascii')
                game_type = 'game1' if reply == '1' else 'game2'
                new_skt.send(b"ask_for_username")
                username = new_skt.recv(1024).decode('ascii')
                
                room_dict[room_idx] = [pub_or_pri, username, 'waiting', game_type]
                user_dict[username][1] = 'in_room'
                print(f"change user {username}'s state to in_room.") # test
                room_created_msg = f"Room created successfuly! The room id is {room_idx}."
                room_idx += 1
                new_skt.send(room_created_msg.encode())
                break
            elif action == 'J':
                
                co = 0
                public_rooms = "\nroom_idx | private/public | roomhost | status    | game\n"
                public_rooms += "----------------------------------------------------\n"
                for idx, values in room_dict.items():
                    if values[2] == 'waiting' and values[0] == 'public':
                        co += 1
                        public_rooms += f"{idx:<8} | {values[0]:<14} | {values[1]:<8} | {values[2]:<9} | {values[3]}\n"
                if co == 0:
                    new_skt.send(b"No public game rooms available")
                    print("No public rooms available")
                    new_skt.close()
                    break
                else: # there's room available
                    print(public_rooms) # test
                    public_rooms += "\nWhich public room do you want to join? Please enter room id: "
                    new_skt.send(public_rooms.encode())
                    valid_room = False
                    while not valid_room:
                        public_room_id = int(new_skt.recv(1024).decode('ascii'))
                        if room_dict[public_room_id][2] != 'waiting':
                            
                            room_full_err = 'The room is full. Please choose another public waiting room. \n'
                            print("tell player to choose another room.") # test
                            new_skt.send(room_full_err.encode())
                        else:
                            valid_room = True
                            print("Valid room found!")
                            
                    # the room is valid to join
                    public_room_game_type = room_dict[public_room_id][3]
                    new_skt.send(public_room_game_type.encode())
                    username = new_skt.recv(1024).decode('ascii')
                    new_skt.close()
                    connected = False
                    time.sleep(1)

                    try:
                        room_host_ip = user_dict[room_dict[public_room_id][1]][2]
                        room_host_port = user_dict[room_dict[public_room_id][1]][3]
                        print(f"room_host ip: {room_host_ip}, port: {room_host_port}") # test
                        new_skt, connected = build_connection(MY_IP,40171,room_host_ip,room_host_port + 1) # room host port or + 1?
                    except Exception as e:
                        print(e)
                        print("Fail to reconnect to the public room host.")
                    
                    if connected:
                        new_skt.send(b"Another player is found!")
                        new_skt.close()

                        try:
                            # give room addr to person to join
                            print(f"player 2 ip: {user_dict[username][2]}, port: {user_dict[username][3]}") # test
                            new_skt, connected = build_connection(MY_IP,40173,user_dict[username][2],user_dict[username][3])
                            if connected:
                                print("will tell the person to join room information!")
                                
                                room_dict[public_room_id][2] = 'in_game'
                                room_dict[public_room_id].append(username)

                                game_ip = room_host_ip
                                game_port = str(room_host_port + 1)
                                
                                new_skt.send(game_ip.encode())
                                _ = new_skt.recv(1024).decode('ascii') # discard the return msg
                                new_skt.send(game_port.encode())
                                _ = new_skt.recv(1024).decode('ascii') # game port received success
                                new_skt.send(public_room_game_type.encode())
                                _ = new_skt.recv(1024).decode('ascii') # game type received success
                                user_dict[room_dict[public_room_id][1]][1] = 'in_game'
                                user_dict[username][1] = 'in_game'

                                new_skt.close()
                                connected = False
                                time.sleep(5)
                                break
                        except Exception as e:
                            print(e)
                            print("Fail to connect to player 2 (want to convey room host address)")
    
                    break
            elif action == 'I': # invite
                player_str = "\n     username     |  state  \n"
                player_str += "-----------------------------\n"
                for idx, values in user_dict.items():
                    if values[1] != "log_out":
                        player_str += f"{idx:<17} | {values[1]}\n"
                print(user_dict) # test
                new_skt.send(player_str.encode())
                # person_to_invite = new_skt.recv(1024).decode('ascii')
                while True:
                    person_to_invite = new_skt.recv(1024).decode('ascii')
                    # print(person_to_invite)
                    if person_to_invite in user_dict:
                        break
                    else:
                        new_skt.send(b"Player not found.")
                
                new_skt.send(b"okay, give me username.")
                inviter_addr = addr
                inviter_name = new_skt.recv(1024).decode('ascii')
                
                new_skt.close()
                connected = False
                time.sleep(1) # wait for new_skt being properly closed
                # connect to the player to invite
                try:
                    new_skt, connected = build_connection(MY_IP,40170,user_dict[person_to_invite][2],user_dict[person_to_invite][3]+2)
                    print("Successfully connect with the person to invite. Ready to send the invitation.")
                    print(f"person_to_invite ip: {user_dict[person_to_invite][2]}, port: {user_dict[person_to_invite][3] + 2}")
                except Exception as e:
                    print(e)
                    print("Server fails to connect with the person you want to invite. Please try again later.")

                if connected:
                    # send inviter's ip and port
                    invitation = f"{inviter_name} wants to invite you to join the game room. Accept the invitation? (Y/N): "
                    new_skt.send(invitation.encode())
                    join_or_not = new_skt.recv(1024).decode('ascii')
                    
                    new_skt.close()
                    connected = False
                    time.sleep(3)

                    try:
                        print(inviter_addr)
                        new_skt, connected = build_connection(MY_IP,40171,inviter_addr[0],inviter_addr[1]+1)
                    except:
                        print("Fail to reconnect to the inviter.")

                    if connected:
                        new_skt.send(join_or_not.encode())
                        new_skt.close()
                        connected = False
                        time.sleep(1)
                        if join_or_not == 'N':
                            break
                        else: # the invitation is accepted
                            try:
                                new_skt, connected = build_connection(MY_IP,40170,user_dict[person_to_invite][2],user_dict[person_to_invite][3]+2)
                            except:
                                print("Fail to reconnect to the person to invite, 2nd phase.")

                            if connected:
                                print("will tell the person to invite room information!")
                                game_type = 'no_game'
                                for idx, values in room_dict.items(): # update the room status
                                    if values[1] == inviter_name and values[2] != 'dissolve':
                                        room_dict[idx][2] = 'in_game' # change the room's state
                                        room_dict[idx].append(person_to_invite) # add another player to the end of the room list of the room
                                        game_type = room_dict[idx][3]
                                        break
                                if game_type == 'no_game':
                                    print("game type not exist, default game1")
                                game_type = 'game1' if game_type == 'no_game' else game_type
                                game_ip = inviter_addr[0]
                                game_port = str(inviter_addr[1] + 1)
                                
                                new_skt.send(game_ip.encode())
                                _ = new_skt.recv(1024).decode('ascii') # discard the return msg
                                new_skt.send(game_port.encode())
                                _ = new_skt.recv(1024).decode('ascii') # game port received success
                                new_skt.send(game_type.encode())
                                _ = new_skt.recv(1024).decode('ascii') # game type received success
                                print(_) # test: game type received
                                user_dict[inviter_name][1] = 'in_game'
                                user_dict[person_to_invite][1] = 'in_game'

                                new_skt.close()
                                connected = False
                                time.sleep(5)
                                break

            elif action == 'NE':
                new_skt.send(b"give_me_username")
                username = new_skt.recv(1024).decode('ascii')
                for idx, values in room_dict.items():
                    if values[1] == username and values[2] != 'dissolve':
                        user_dict[username][1] = 'idle'
                        user_dict[values[4]][1] = 'idle'
                        room_dict[idx][2] = 'dissolve' # dissolve the room
                        print(f"Dissolve the room id {idx}")
                        break
                break
            elif action == 'LO':
                new_skt.send(b"give_me_username")
                username = new_skt.recv(1024).decode('ascii')
                user_dict[username][1] = 'log_out'
                new_skt.send(b"Log out successfully!")
                break
            else:
                print("This action is not yet implemented./The client disconnects.")
                break
        
        new_skt.close()
