from Server import Server
from Client import Client
import threading


server = Server('127.0.0.1',17200) # update to real ip
client = Client('local host',14200) # update to real ip

client_thread = threading.Thread(target=client.start_client)
server_thread = threading.Thread(target=server.send_offers_to_clients)
server_thread.start()
client_thread.start()

