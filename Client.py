from socket import *
import struct
import time
import threading
import msvcrt


class Client:

    def __init__(self):
        """
        Constructor
        """
        self.client_udp = socket(AF_INET, SOCK_DGRAM) # init udp socket
        self.client_udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.client_udp.bind(('', 13117))
        self.name = 'HoneyPot\n' # init name of group
        self.stop_sending_keys = False
        print("client started, listening for offer requests")

    def start_client(self):
        """
        This methon is the main thread of the client which runs forever.
        It connects to a server and then compete in the game
        :return:
        """
        while True:
            try:
                data, sender_address = self.client_udp.recvfrom(8) # receive brodcast message from server
                decoded_message = struct.unpack('Ibh', data) # decode brodcast message in format int,int int
                if decoded_message[0] != 0xfeedbeef: # if decoded message doesn't start with this
                    continue
                print("received offer from " + sender_address[0] + ", attempting to connect...")
                port = decoded_message[2]
                try:
                    self.client_tcp = socket(AF_INET, SOCK_STREAM)
                    self.client_tcp.connect((sender_address[0], port)) # connect to server
                    self.client_tcp.sendall(self.name.encode()) # send the server the name of the group
                    self.play_game() # play game
                    self.stop_sending_keys = False
                    self.client_tcp.close() # close connection with server
                    print("Server disconnected, listening for offer requests")
                except error:  # if failed to connect to server
                    continue
            except struct.error: # if failed to decode data
                continue

    def play_game(self):
        """
        This function controls the game of the client
        :return:
        """
        self.client_tcp.settimeout(22)
        try:
            data = self.client_tcp.recv(4096) # wait to receive welcome message
            if not data:  # if connection closed
                self.client_tcp.close()
                return
            decoded_data = data.decode()
            print(decoded_data)
            timer_thread = threading.Thread(target=self.timer) # init 10 second tomer thread
            timer_thread.start()
            while not self.stop_sending_keys:
                if msvcrt.kbhit():
                    self.client_tcp.sendall(msvcrt.getch()) # press on keyboard key

        except error:
            self.client_tcp.close()

    def timer(self):
        """
        Timer function
        :return:
        """
        time.sleep(10)
        self.stop_sending_keys = True


