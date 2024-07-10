import socket 
import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Create a server sie socket using IPv4 (AF_INET) and TCP protocol (SOCK_STREAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print(socket.gethostname()) # Get host name (device)
# print(socket.gethostbyname(socket.gethostname())) # Get ID address of host
# bind our new socket to a tuple (IP Address, Port Add)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] Message recieved: {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()
        

def start():
    # put socket into listening mode to listen for any possible connections
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        # conn.send("You are connected".encode(FORMAT))
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        
print("[STARTING] server is starting...")
start()
