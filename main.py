from Server import Server
from Client import Client
import threading
from scapy.all import get_if_addr
from constants import *

ip = get_if_addr(ETH2)
server = Server(ip, PORT)
client = Client()
server_thread = threading.Thread(target=server.start_server)
client_thread = threading.Thread(target=client.start_client)
server_thread.start()
client_thread.start()
