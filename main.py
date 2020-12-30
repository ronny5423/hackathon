from Server import Server
from Client import Client
import threading
import sys
from scapy.all import get_if_addr

# choose network
# args_lst = sys.argv
# network = args_lst[1]
# if not network:
#     ip = get_if_addr('uth1')
# else:
#     ip = get_if_addr(network)

server = Server('127.0.0.1',2130)
server_thread = threading.Thread(target=server.start_server)
client_threads = []
# for i in range(3):
#     client = Client()
#     client_threads.append(threading.Thread(target=client.start_client))
client = Client()
client_thread = threading.Thread(target=client.start_client)
server_thread.start()
# for thread in client_threads:
#     thread.start()
client_thread.start()

