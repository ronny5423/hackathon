import socket

class Server:
    def __init__(self,ip,port):
        self.udp_socket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
        self.ip =ip
        self.port = port


    def listen_to_clients(self):
        self.udp_socket.bind((self.ip,self.port))
        while True:
            


    def