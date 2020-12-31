from socket import *
import struct
import time
import threading
#import msvcrt
import getch
import multiprocessing
from constants import *

class Client:

    def __init__(self):
        """
        Constructor
        """
        self.name = 'Honeypot\n' # init name of group
        self.stop_sending_keys = False


    def start_client(self):
        """
        This methon is the main thread of the client which runs forever.
        It connects to a server and then compete in the game
        :return:
        """
        while True:
            try:
                self.client_udp = socket(AF_INET, SOCK_DGRAM)  # init udp socket
                self.client_udp.bind(('', UDP_DEST_PORT))
                print("\033[{}client started, listening for offer requests\033[0m".format(CLIENT_COLOR))
                data, sender_address = self.client_udp.recvfrom(8) # receive brodcast message from server
                decoded_message = struct.unpack('IbH', data) # decode brodcast message in format int,int int
                if decoded_message[0] != COOKIE or decoded_message[1] != MESSAGE_TYPE: # if decoded message doesn't start with this
                    continue
                print("\033[{0}received offer from {1},"
                      " attempting to connect...\033[0m".format(CLIENT_COLOR, sender_address[0]))

                port = decoded_message[2]
                try:
                    self.client_tcp = socket(AF_INET, SOCK_STREAM)
                    self.client_tcp.connect((sender_address[0], port)) # connect to server
                    try:
                        self.client_tcp.sendall(self.name.encode()) # send the server the name of the group
                    except:
                        self.client_tcp.close()
                        self.client_udp.close()
                        continue
                    self.play_game() # play game
                    self.stop_sending_keys = False
                    self.client_tcp.close() # close connection with server
                    print("\033[{}Server disconnected, listening for offer requests\033[0m".format(SERVER_DIS))
                except:
                    self.client_udp.close()
                    continue

            except: # if thrown any error(connection,decode,etc...)
                self.client_udp.close()
                continue

            self.client_udp.close()

    def play_game(self):
        """
        This function controls the game of the client
        :return:
        """
        self.client_tcp.settimeout(22)
        buffer = 4096
        try:
            data = self.client_tcp.recv(buffer) # wait to receive welcome message
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
                game_over_message = self.client_tcp.recv(buffer)
                if not game_over_message:
                    return
                decoded_message = game_over_message.decode()
                print("\033[{0}{1}\033[0m".format(SERVER_COLOR, decoded_message))
            except:
                return

        except:
            return

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
        try:
            self.client_tcp.sendall(getch.getch().encode())
            #self.client_tcp.sendall(msvcrt.getch())  # press on keyboard key
        except:
            pass
