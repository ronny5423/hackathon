from Server import Server
from Client import Client
import threading
from scapy.all import get_if_addr

#ip = get_if_addr('uth1')
server = Server('127.0.0.1',2130)
client = Client()
server_thread = threading.Thread(target=server.start_server)
client_thread = threading.Thread(target=client.start_client)
server_thread.start()
client_thread.start()

