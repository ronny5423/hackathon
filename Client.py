from socket import *
import struct
import time
import threading
# import msvcrt
import getch
import multiprocessing


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
        print("\033[0;95mclient started, listening for offer requests\033[0m")

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
                print("\033[0;95mreceived offer from {}, attempting to connect...\033[0m".format(sender_address[0]))

                port = decoded_message[2]
                try:
                    self.client_tcp = socket(AF_INET, SOCK_STREAM)
                    self.client_tcp.connect((sender_address[0], port)) # connect to server
                    if self.client_tcp.fileno() != -1: # check if connection not closed
                        self.client_tcp.sendall(self.name.encode()) # send the server the name of the group
                    self.play_game() # play game
                    self.stop_sending_keys = False
                    self.client_tcp.close() # close connection with server
                    print("\033[0;31mServer disconnected, listening for offer requests\033[0m")
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
               sending_key_thread = multiprocessing.Process(target=self.sending_key_thread)
               sending_key_thread.start()
               sending_key_thread.join(0.5)
               if sending_key_thread.is_alive():
                   sending_key_thread.terminate()

            self.client_tcp.settimeout(5)
            try:
                game_over_message = self.client_tcp.recv(4096)
                if not game_over_message:
                    return
                decoded_message = game_over_message.decode()
                print("\033[1;33m{}\033[0m".format(decoded_message))
            except:
                return


        except error:
            self.client_tcp.close()

    def timer(self):
        """
        Timer function
        :return:
        """
        time.sleep(10)
        self.stop_sending_keys = True

    def sending_key_thread(self):
        """
        sending key thread function
        :return:
        """
        if self.client_tcp.fileno() != -1:
            self.client_tcp.sendall(getch.getch().encode())
            # self.client_tcp.sendall(msvcrt.getch())  # press on keyboard key



