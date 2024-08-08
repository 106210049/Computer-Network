import socket

HOST_IP=socket.gethostbyname(socket.gethostname())
HOST_PORT=12345
ENCODER="utf-8"
BYTE_SIZE=1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST_IP,HOST_PORT))

while True:
    # Recieve information from server
    message=client.recv(BYTE_SIZE).decode(ENCODER)
    if(message=="quit"):
        client.send("quit".encode(ENCODER))
        print("\n Ending chat ... goodbye")
        break
    else: 
        print(f"\n {message}")
        message=input("Message ->: ")
        client.send(message.encode(ENCODER))

client.close()