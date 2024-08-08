import socket

HOST_IP=socket.gethostbyname(socket.gethostname())
HOST_PORT=12345
ENCODER="utf-8"
BYTE_SIZE=1024

# Create a server sie socket using IPv4 (AF_INET) and TCP protocol (SOCK_STREAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind our new socket to a tuple (IP Address, Port Add)
server.bind((HOST_IP,HOST_PORT))

server.listen()

print("Server is running ... \n")

client_socket, client_server=server.accept()
client_socket.send("You are connected to server ... \n".encode(ENCODER))

# Send/recieve message:

while True:
    #recieve information from the client
    message=client_socket.recv(BYTE_SIZE).decode(ENCODER)

    if message=="quit":
        client_socket.send("quit".encode(ENCODER))
        print("\n Ending chat ... goodbye")
        break
    else: 
        print(f"\n {message}")
        message=input("Message ->: ")
        client_socket.send(message.encode(ENCODER))

# Close sọcket
server.close()