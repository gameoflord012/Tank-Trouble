import socket
import threading
import pickle

#server
HOST = '0.0.0.0'
PORT = 65432
MAX_PLAYERS = 2

threads = []
clients_cnn = []

def start_server():
    global g_socket

    g_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    g_socket.bind((HOST, PORT))
    print("PVP tank server started \nBinding to port", PORT)
    g_socket.listen(2) 
    accept_players()
    
def accept_players():
    global threads

    for i in range(MAX_PLAYERS):
        conn, addr = g_socket.accept()
        clients_cnn.append(conn)
        print(f'You are player {addr}')

        # create connection handle thread for each client
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        threads.append(thread)

    for thread in threads:
        thread.join()

def handle_client(conn, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            print(f"Connection {addr} closed")
            break

        try:
            key_states = pickle.loads(data)
        except pickle.UnpicklingError:
            continue
        
        print(f"Data received from {addr}")

        player_index = clients_cnn.index(conn)

        if(player_index == 1):
            key_states[0], key_states[1] = key_states[1], key_states[0]

        # send back to sender 
        conn.sendall(pickle.dumps(key_states))

        # send to other player
        if(len(clients_cnn) == 2):
            clients_cnn[1 - player_index].sendall(pickle.dumps(key_states))

start_server()
