import socket

UDP_IP = '0.0.0.0'
UDP_PORT = int(input("Please enter which port you want to set the server on: "))

start_game = False
wait_for_invitation = True
tcp_server_addr = () # tuple
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((UDP_IP, UDP_PORT))
    msg, addr = s.recvfrom(1024) # longest msg we can recv is 1024 bytes
    # print(msg.decode('ascii'), end="") # test
    msg = msg.decode()
    if msg == 'give_me_your_ip_and_port' or msg.startswith("Invite Request"): # the client is searching for players
        if msg == 'give_me_your_ip_and_port':
            s.sendto("iamhere".encode(), addr)
            s.settimeout(0.1) # so that almost everyone can search for it
        try:
            if msg == 'give_me_your_ip_and_port':
                while True:
                    invitation, addr1 = s.recvfrom(1024) # receive invitation
                    invitation = invitation.decode()
                    if addr1 == addr:
                        break
                    else:
                        print(f"msg from other address: {addr1[0]}, {addr1[1]}")
            else:
                invitation = msg
            # print(f"addr: {addr}, addr1: {addr1}")

            while True:
                print(invitation, end="")
                response = input()
                if response == "yes":
                    s.sendto(response.encode(), addr)
                    print("Loading...")

                    while True:
                        tcp_port, new_addr = s.recvfrom(1024)
                        tcp_port = tcp_port.decode('ascii')
                        if new_addr == addr: 
                            # print(f"Will connect to tcp_port: {tcp_port}")
                            start_game = True
                            tcp_server_addr = addr
                            wait_for_invitation = False
                            s.close()
                            break
                        else:
                            print(f"msg from another addr {new_addr[0]}, {new_addr[1]} (can be ignored): {tcp_port}")
                    break
                elif response == "no":
                    s.sendto(response.encode(), addr)
                    print("Wait for other invitations...")
                    s.close()
                    break
                else:
                    print("Incorrect input.")
            if not wait_for_invitation:
                break
        except TimeoutError:
            print("Still waiting for invitations...")
            continue
    else:
        print(f"msg that we can ignore: {msg.decode()}")
        s.close()
# s.close() # close the udp socket

if start_game:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create tcp socket
    s.bind((UDP_IP, UDP_PORT))
    s.connect(tcp_server_addr)
    choice = input("Please enter your choice (1:rock/2:paper/3:scissors): ")
    s.send(choice.encode())
    print("Waiting for server's response...")
    result = s.recv(1024).decode('ascii')
    print(result)
