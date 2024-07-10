import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostname()  # as both code is running on same pc
ADDR = (SERVER, PORT)

# Create a server sie socket using IPv4 (AF_INET) and TCP protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(socket.gethostname()) # Get host name (device)
print(socket.gethostbyname(socket.gethostname())) # Get ID address of host
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

while True:
    msg=input("->")
    
    if(msg=="disconnect"):
        break
    send(msg)
    
send(DISCONNECT_MESSAGE)
