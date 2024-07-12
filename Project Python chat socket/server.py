import socket
import threading


class ChatServer:
    def __init__(self):
        self.server_socket = None
        self.rooms = {}  # Dictionary to store chat rooms
        self.create_listening_server()

    def create_listening_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket using TCP port and ipv4
        local_ip = '127.0.0.1'
        local_port = 10319
        # this will allow you to immediately restart a TCP server
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # this makes the server listen to requests coming from other computers on the network
        self.server_socket.bind((local_ip, local_port))
        print("Listening for incoming messages..")
        self.server_socket.listen(10)  # listen for incoming connections / max 10 clients
        self.receive_connections_in_a_new_thread()

    def receive_messages(self, client_socket, room_name):
        while True:
            try:
                incoming_buffer = client_socket.recv(256)  # initialize the buffer
                if not incoming_buffer:
                    break
                message = incoming_buffer.decode('utf-8')
                if message.startswith("left:"):
                    self.remove_from_clients_list(client_socket, room_name)
                    break
                else:
                    self.broadcast_to_room(message, room_name, client_socket)
                print(message)
            except:
                self.remove_from_clients_list(client_socket, room_name)
                break

        client_socket.close()

    def broadcast_to_room(self, message, room_name, senders_socket):
        for client_socket in self.rooms.get(room_name, []):
            if client_socket is not senders_socket:
                try:
                    client_socket.sendall(message.encode('utf-8'))
                except:
                    client_socket.close()
                    self.remove_from_clients_list(client_socket, room_name)

    def receive_connections_in_a_new_thread(self):
        while True:
            client_socket, (ip, port) = self.server_socket.accept()
            print('Connected to ', ip, ':', str(port))
            
            # Expect the client to send the room name first
            room_name = client_socket.recv(256).decode('utf-8')
            print(f'Client joined room: {room_name}')
            
            if room_name not in self.rooms:
                self.rooms[room_name] = []
            self.add_to_clients_list(client_socket, room_name)

            t = threading.Thread(target=self.receive_messages, args=(client_socket, room_name))
            t.start()

    def add_to_clients_list(self, client_socket, room_name):
        if client_socket not in self.rooms[room_name]:
            self.rooms[room_name].append(client_socket)
            self.broadcast_client_count(room_name)

    def remove_from_clients_list(self, client_socket, room_name):
        if client_socket in self.rooms.get(room_name, []):
            self.rooms[room_name].remove(client_socket)
            self.broadcast_client_count(room_name)

    def broadcast_client_count(self, room_name):
        message = f"count:{len(self.rooms[room_name])}"
        for client_socket in self.rooms.get(room_name, []):
            try:
                client_socket.sendall(message.encode('utf-8'))
            except:
                self.remove_from_clients_list(client_socket, room_name)


if __name__ == "__main__":
    ChatServer()
