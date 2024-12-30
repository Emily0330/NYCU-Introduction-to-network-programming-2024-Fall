import socket

linux_server = input("Which linux server are you on? (1, 2, 3, or 4): ")
MY_IP = f"140.113.235.15{linux_server}"
MY_PORT = 40169

name = input("Please input your name: ")

players_cnt = 0
print("Searching for waiting players...")
for i in range(1,5):
    server_ip = f"140.113.235.15{i}"
    for port in range(50131, 50152):
        server = (server_ip, port)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((MY_IP,MY_PORT))
        s.sendto("give_me_your_ip_and_port".encode(), server)
        s.settimeout(0.1) # one second to wait for the response
        while True:
            try:
                player, player_addr = s.recvfrom(1024)
                # print(f"player: {player.decode()}") # test
                if player.decode() == "iamhere":
                    players_cnt += 1
                    print(f"Server IP: {server_ip}/Server Port: {port}")
                    break
            except TimeoutError:
                break
s.close()

if players_cnt == 0:
    print("No players found. QAQ")
else:
    print("Please enter the player IP and port you want to invite.")
    player_IP = input("Player IP: ")
    player_port = int(input("Player port:"))
    server = (player_IP, player_port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # new socket to recv
    s.bind((MY_IP, MY_PORT)) # bind the socket to receive response
    s.sendto(f'Invite Request: {name} invites you to play the game, accept the invitation? (yes/no)'.encode(), server)
    print("Waiting response...")
    player_found = False

    while True:
        response, addr = s.recvfrom(1024) # longest msg we can recv is 1024 bytes
        # print(f'addr:{addr}')
        response = response.decode('ascii')
        if addr[0] == player_IP:
            if response == "yes":
                player_found = True
            else:
                print("The person does not want to play the game QAQ")
            break
        else:
            print(f"You can ignore this msg: {response}")
            continue
    if player_found:
        # print("UDP sucess!")
        # start TCP protocol
        tcp_port = input("Please enter your TCP port to start the game: ")
        s.sendto(tcp_port.encode(), server)
        s.close() # close the udp socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a TCP socket
        s.bind((MY_IP, MY_PORT))
        s.listen(1) # only accept one connection at the same time
        print("TCP server starts, waiting for the client to connect...")
        
        new_skt, addr = s.accept() # use the returned skt to receive and send data
        print(f"Connected with client at ip {addr[0]}, port {addr[1]}")
        print("The game is started! Waiting for client's input...")

        client_choice = new_skt.recv(1024).decode('ascii')
        if len(client_choice) == 0: 
            print("Client closed the connection")

        choice = input("Please enter your choice (1:rock/2:paper/3:scissors): ")

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

        new_skt.send(client_msg.encode())
        s.close() # close the tcp socket




# s.close()