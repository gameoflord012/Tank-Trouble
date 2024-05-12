import socket
import threading
import pickle

#server
HOST = 'localhost'
PORT = 65432

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

    for i in range(1):
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

        # send back to sender 
        conn.sendall(pickle.dumps(key_states))

        if(len(clients_cnn) < 2):
            continue

        # send to other player
        key_states[0], key_states[1] = key_states[1], key_states[0]
        clients_cnn[1 - clients_cnn.index(conn)].sendall(pickle.dumps(key_states))

start_server()
