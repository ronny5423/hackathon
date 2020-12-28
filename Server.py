import socket
import threading
import time
import struct


class Server:
    def __init__(self, ip, port):
        """
        Constructor
        :param ip: str,ip of the server
        :param port: int,tcp port of the server
        """
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.kill_listening_thread = False
        self.kill_client_game_thread = False
        self.group_counters = [0,0]

    def start_server(self):
        """
        This function is the main thread of the server
        :return:
        """
        # init all server sockets
        self.udp_socket.bind((self.ip, 15200))
        self.tcp_socket.bind((self.ip, self.port))
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print('Server started, listening on IP address ' + str(self.ip))

        while True:
            connected_clients = []
            group_names = {}
            self.kill_listening_thread = False
            self.kill_client_game_thread = False
            brodcast_message_thread = threading.Thread(target=self.send_brodcast_message, args=[
                struct.pack('IbH', 0xfeedbeef, 0x2, self.port)])  # init sending brodcast messages thread
            listen_to_clients_thread = threading.Thread(target=self.listen_to_clients, args=[connected_clients,
                                                                                             group_names])  # init listening to clients thread
            brodcast_message_thread.start()
            listen_to_clients_thread.start()
            brodcast_message_thread.join()
            self.kill_listening_thread = True
            listen_to_clients_thread.join()
            self.create_game(connected_clients, group_names)

    def send_brodcast_message(self, message, counter=10):
        """
            This function is a sending brodcast messages thread. It sends brodcast messages for 10 seconds
        :param message: str,brodcast message
        :param counter: int,counter that counts the number of sends left
        :return:
        """
        while counter > 0:
            self.udp_socket.sendto(message, ('255.255.255.255', 13117))
            print("sending brodcast message")
            time.sleep(1)
            counter -= 1

    def listen_to_clients(self, connected_clients, group_names):
        """
            This function is the listening to clients thread. It listens to clients for 10 seconds on tcp
            :param connected_clients:list,a list that will hold all the connected clients
            :param group_names:dict, a dictionary of the group names
            :return:
            """
        threads = []
        lock = threading.Lock()
        lock1 = threading.Lock()
        self.tcp_socket.settimeout(3)
        while not self.kill_listening_thread:
            try:
                self.tcp_socket.listen()
                client, address = self.tcp_socket.accept()
                with lock1:
                    connected_clients.append(client)

                get_name_thread = threading.Thread(target=self.recieve_name_from_client,
                                                   args=[client, group_names, lock, connected_clients,
                                                         lock1])  # init listening to client's group name thread
                threads.append(get_name_thread)
                get_name_thread.start()
            except socket.timeout:
                continue

        for thread in threads:  # wait till all group names were sent
            thread.join()

    def recieve_name_from_client(self, client_socket, names_dic, lock, connected_clients, lock1):
        """
        Receive client's group name thread
        :param client_socket: socket,client socket
        :param names_dic: dict,dictionary of group names
        :param lock: Lock,lock to use to write to groups names dictionary
        :param connected_clients: list, a list of connected clients
        :param lock1: lock, lock to write to connected clients list
        :return:
        """
        client_socket.settimeout(3)
        name = ''
        try:
            while True:
                data = client_socket.recv(1024)  # receive data from client
                if not data:  # if client is not connected
                    client_socket.close()
                    with lock1:  # remove disconnected client from connected clients list
                        connected_clients.remove(client_socket)
                    return
                try:
                    encoded_data = data.decode()
                    if '\n' in encoded_data:  # if it is the end of the name
                        name += encoded_data[:-1]
                        break
                    name += encoded_data
                except UnicodeError:  # if data wasn't in the expected format,close the connection
                    client_socket.close()
                    with lock1:
                        connected_clients.remove(client_socket)
                        return
            with lock:  # add name to names dict
                names_dic[client_socket] = name

        except socket.timeout:
            client_socket.close()
            with lock1:
                connected_clients.remove(client_socket)  # remove disconnected client from connected clients list

    def create_game(self, connected_clients, group_names):
        """
        This function creates the game
        :param connected_clients: list,list of connected clients
        :param group_names: dict,a dictionary of group names
        :return:
        """
        if len(connected_clients) == 0:  # if no clients were connected
            return

        participants_in_each_group = int(len(connected_clients) / 2)  # calculate number of participants in each group
        group1 = connected_clients[:participants_in_each_group + 1]
        group2 = connected_clients[participants_in_each_group + 1:]
        group1_input = []
        group2_input = []
        # init welcome message
        welcome_message_to_clients = 'Welcome to destroying keyboard game:)\nGroup 1:\n==\n'
        welcome_message_to_clients = self.init_dict_input_for_each_group(group1, group1_input,
                                                                         welcome_message_to_clients, group_names)
        welcome_message_to_clients += 'Group 2:\n==\n'
        welcome_message_to_clients = self.init_dict_input_for_each_group(group2, group2_input,
                                                                         welcome_message_to_clients, group_names)
        welcome_message_to_clients += 'start pressing keys on keyboard as fast as you can for 10 seconds\n'
        threads = []
        group1_counter_lock = threading.Lock()
        group2_counter_lock = threading.Lock()
        self.init_threads_for_client_game_communication(threads, welcome_message_to_clients, group1, group1_input,group1_counter_lock,0)
        self.init_threads_for_client_game_communication(threads, welcome_message_to_clients, group2, group2_input,group2_counter_lock,1)
        # start communicating with each client
        for thread in threads:
            thread.start()
        time.sleep(10)
        self.kill_client_game_thread = True
        # finish sending keys
        for t in threads:
            t.join()

        self.print_relevant_end_game_data(group1_input, group2_input, group_names, group1, group2)
        # close connections with clients
        for client in connected_clients:
            client.close()
        self.group_counters = [0,0]
        print("Game over, sending out offer requests...")

    def print_relevant_end_game_data(self, group1_input, group2_input, group_names, group1, group2):
        """
        This function prints the relevant after game information
        :param group1_input: list, list of group1 keys dictionary
        :param group2_input: list, list of group2 keys dictionary
        :param group_names: dict,dictionary of group names
        :param group1: list,list of clients in group 1
        :param group2: list,list of clients in group 2
        :return:
        """
        # score_group1 = self.compute_score_for_group(group1_input)
        # score_group2 = self.compute_score_for_group(group2_input)

        fastest_group = 0
        fastest_group_lst = []
        if self.group_counters[0] > self.group_counters[1]:
            fastest_group = 1
            fastest_group_lst = group1
        else:
            fastest_group = 2
            fastest_group_lst = group2
        print("Game over!")
        print("Group" + str(fastest_group) + " was the fastest. Very good Group" + str(fastest_group) + "!")
        print("Group1 typed " + str(self.group_counters[0]) + " chars, Group2 typed " + str(self.group_counters[1]) + " chars")
        print("The winners are:")
        for client in fastest_group_lst:
            print(group_names[client])

    def init_dict_input_for_each_group(self, group, group_input_list, welcome_message, group_names):
        """
        This function inits input dictionary for each lient in the group
        :param group: list,list of the clients in the group
        :param group_input_list: list,list of dictionary to each client in the group
        :param welcome_message: str,welcome message to concat
        :param group_names:dict,a dictionary of group names
        :return:
        """
        for client in group:
            group_input_list.append({})
            welcome_message += group_names[client]
            welcome_message += '\n'
        return welcome_message

    def init_threads_for_client_game_communication(self, threads_list, welcome_message, group, group_input_dicts,group_counter_lock,counter_index):
        """
        This function init the thread for each client
        :param counter_index: int,index of the group counter
        :param threads_list: list,list of clients threads
        :param welcome_message: str,welcome message to send to client
        :param group: list,a list of the clients in the group
        :param group_input_dicts: list,a list of the keys dictionaries of the group
        :return:
        """
        index = 0
        for client in group:
            threads_list.append(threading.Thread(target=self.communicate_with_client_in_game,
                                                 args=[welcome_message, client, group_input_dicts[index],group_counter_lock,counter_index]))
            index += 1

    def compute_score_for_group(self, group_input):
        """
        This function computes the score for each group
        :param group_input: list, a list of keys dictionaries of each group
        :return:
        """
        score = 0
        for client_dict in group_input:
            for key in client_dict:
                score += client_dict[key]
        return score

    def communicate_with_client_in_game(self, welcome_message_to_send, client_socket, keys_lst,group_counter_lock,index):
        """
        A thread to communicate with the client during the game
        :param index: int,index of the counter of the group
        :param group_counter_lock: Lock,a lock to write to group counter
        :param welcome_message_to_send: str,welcome message to send to client
        :param client_socket: socket,client socket
        :param keys_lst: dict,a dictionary where each client stores the keys he pressed
        :return:
        """
        client_socket.sendall(welcome_message_to_send.encode())  # send welcome message
        client_socket.settimeout(1)
        while not self.kill_client_game_thread:
            try:
                data = client_socket.recv(100)  # receive pressed key
                if not data:  # if connection is close
                    client_socket.close()
                    return
                decoded_data = data.decode()  # decode key
                if len(decoded_data) != 1:  # if the key is longer than a single char
                    continue
                if decoded_data in keys_lst:  # if key in the dictionary
                    keys_lst[decoded_data] += 1
                else:  # if not
                    keys_lst[decoded_data] = 1
                with group_counter_lock:
                    self.group_counters[index] += 1
            except UnicodeError:
                continue
            except socket.error:
                continue
