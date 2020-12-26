from socket import *

class Client:

    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.client_udp = socket(AF_INET,SOCK_DGRAM)
        self.client_tcp = socket(AF_INET,SOCK_STREAM)
        self.client_udp.bind(('',13117))
        self.name = 'Yossi is the king!'
        print("client started, listening for offer requests")



    def start_client(self):
            while True:
                data,sender_address = self.client_udp.recvfrom(20)
                print("received offer from " +sender_address[0]+", attempting to connect...")
                port = int(data[15:])
                try:
                    self.client_tcp.connect((sender_address[0], port))
                    self.client_tcp.send(self.name.encode())
                    self.play_game()
                    print("connected to server")
                except error: # if failed to connect to server
                    print("failed to connect to server "+sender_address[0])



    def play_game(self):
        pass


