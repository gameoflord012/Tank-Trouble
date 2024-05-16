import socket
import threading
import pickle

#server
HOST = '0.0.0.0'
PORT = 65432
MAX_PLAYERS = 2

threads = []
clients_cnn = [None, None]

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
        clients_cnn[i] = conn
        print(f'You are player {addr}')

        # create connection handle thread for each client
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        threads.append(thread)

    for thread in threads:
        thread.join()

def handle_client(conn, addr):
    conn_index = clients_cnn.index(conn)

    while True:
        try:
            byte_data = conn.recv(1024)
            
            if not byte_data:
                print(f"Connection {addr} closed")
                g_socket.close()
        except:
            g_socket.close()
            break

        try:
            data = pickle.loads(byte_data)
        except pickle.UnpicklingError:
            print(f"Error unpickling data from {addr}")
            continue
        
        print(f"Data received from {addr}")

        # send self
        conn.sendall(pickle.dumps([conn_index, None, None, None])) # need modify

        # send to other player
        if(clients_cnn[1 - conn_index] != None):
            clients_cnn[1 - conn_index].sendall(pickle.dumps([1 - conn_index, data[0], data[1], data[2]])) # need modify

start_server()