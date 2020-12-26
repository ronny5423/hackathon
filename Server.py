import socket
import sys
import threading
import time


class Server:
    def __init__(self,ip,port):
        self.udp_socket = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
        self.ip =ip
        self.port = port
        self.stop = False


    def send_offers_to_clients(self):
        try:
            self.udp_socket.bind((self.ip,15200))
            self.tcp_socket.bind((self.ip,self.port))
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
            print('Server started, listening on IP address ' + str(self.ip))
        except socket.error:
            print("problem with binding,exiting...")
            sys.exit(-1)
        self.udp_socket.settimeout(10)
        message = b'0xfeedbeef,0x2,'+str(self.port).encode()
        connected_clients = []
        group_names = []
        while not self.stop:
            brodcast_message_thread = threading.Thread(target=self.send_brodcast_message,args=[message])
            listen_to_clients_thread = threading.Thread(target=self.listen_to_clients,args=[connected_clients,group_names])
            brodcast_message_thread.start()
            listen_to_clients_thread.start()
            brodcast_message_thread.join()
            listen_to_clients_thread.join()
            self.create_game(connected_clients)




    def send_brodcast_message(self,message,counter=10):
            while counter>0:
                self.udp_socket.sendto(message, ('255.255.255.255', 13117))
                print("sending brodcast message")
                time.sleep(1)
                counter -= 1

    def listen_to_clients(self,connected_clients,group_names):
            self.tcp_socket.settimeout(10)
            while True:
                try:
                    self.tcp_socket.listen()
                    print("listening to requests")
                    client, address = self.tcp_socket.accept()
                    print("client connected")
                    connected_clients.append(client)
                except socket.timeout:
                    print("timeout")
                    break


    def recieve_name_from_client(self):
        pass



    def create_game(self,connected_clients):
        if len(connected_clients) == 0: # if no clients were connected
            return

        participants_in_each_group = int(len(connected_clients)/2)






    def stop_server(self):
        self.stop = True










