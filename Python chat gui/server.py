import socket
import threading


class ChatServer:
    clients_list = []
    client_count = 0
    previous_client_count = 0  # Biến lưu trữ số lượng client trước khi có thay đổi

    last_received_message = ""

    def __init__(self):
        self.server_socket = None
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
        self.server_socket.listen(5)  # listen for incoming connections / max 5 clients
        self.receive_messages_in_a_new_thread()

    def receive_messages(self, so):
        while True:
            try:
                incoming_buffer = so.recv(256)  # initialize the buffer
                if not incoming_buffer:
                    break
                self.last_received_message = incoming_buffer.decode('utf-8')
                if self.last_received_message.startswith("left:"):
                    # Handle client disconnection
                    self.broadcast_to_all_clients(so)
                    self.remove_from_clients_list(so)
                    break
                else:
                    self.broadcast_to_all_clients(so)  # send to all clients
                print(self.last_received_message)
            except:
                self.remove_from_clients_list(so)
                break

        so.close()

    def broadcast_to_all_clients(self, senders_socket):
        for client in self.clients_list:
            socket, (ip, port) = client
            if socket is not senders_socket:
                try:
                    socket.sendall(self.last_received_message.encode('utf-8'))
                except:
                    socket.close()
                    self.remove_from_clients_list(socket)

    def broadcast_client_count(self):
        message = f"count:{self.client_count}"
        for client_socket, _ in self.clients_list:
            try:
                client_socket.sendall(message.encode('utf-8'))
            except:
                self.remove_from_clients_list(client_socket)

    def receive_messages_in_a_new_thread(self):
        while True:
            client = so, (ip, port) = self.server_socket.accept()
            self.add_to_clients_list(client)
            print('Connected to ', ip, ':', str(port))

            t = threading.Thread(target=self.receive_messages, args=(so,))
            t.start()

    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)
            self.previous_client_count = self.client_count  # Lưu số lượng client trước khi cập nhật
            self.client_count = len(self.clients_list)
            if self.client_count != self.previous_client_count:
                self.broadcast_client_count()
                print(self.client_count)
                
    def remove_from_clients_list(self, client_socket):
        for client in self.clients_list:
            socket, (ip, port) = client
            if socket == client_socket:
                self.clients_list.remove(client)
                self.previous_client_count = self.client_count  # Lưu số lượng client trước khi cập nhật
                self.client_count = len(self.clients_list)
                if self.client_count != self.previous_client_count:
                    self.broadcast_client_count()
                    print(self.client_count)
                break


if __name__ == "__main__":
    ChatServer()
