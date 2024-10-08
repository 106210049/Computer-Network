'''
Note:
    # Fix server video call here            

'''
import socket
import threading
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, StringVar, messagebox
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
from vidstream import StreamingServer
import cv2
import numpy as np
class ChatServer:
    def __init__(self, gui):
        self.server_socket = None
        self.rooms = {}  # Dictionary to store chat rooms
        self.video_call_servers = {}  # Dictionary to store video call servers per room
        self.gui = gui
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
                elif message.startswith("video_call:"):
                    self.start_video_call_server(room_name)
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
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
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

            # Update GUI
            self.gui.update_room_list(self.rooms)

    def add_to_clients_list(self, client_socket, room_name):
        if client_socket not in self.rooms[room_name]:
            self.rooms[room_name].append(client_socket)
            self.broadcast_client_count(room_name)

    def remove_from_clients_list(self, client_socket, room_name):
        if client_socket in self.rooms.get(room_name, []):
            self.rooms[room_name].remove(client_socket)
            self.broadcast_client_count(room_name)
            # Update GUI
            self.gui.update_room_list(self.rooms)

    def broadcast_client_count(self, room_name):
        message = f"count:{len(self.rooms[room_name])}"
        for client_socket in self.rooms.get(room_name, []):
            try:
                client_socket.sendall(message.encode('utf-8'))
            except:
                self.remove_from_clients_list(client_socket, room_name)

    # Fix server video call here            
    def start_video_call_server(self, room_name):
        if room_name not in self.video_call_servers:
            video_port = 10320 + len(self.video_call_servers)
            video_call_server = StreamingServer('127.0.0.1', video_port)
            video_call_server.start_server(3)
            self.video_call_servers[room_name] = video_call_server
            self.broadcast_to_room(f"video_call_started:{video_port}", room_name, None)

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Notify all clients that the server is closing
            for room_name, clients in self.rooms.items():
                for client_socket in clients:
                    try:
                        client_socket.sendall("Server is closing".encode('utf-8'))
                        client_socket.close()
                    except Exception as e:
                        print(f"Error sending close message to client: {e}")

            # Close the server socket
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception as e:
                    print(f"Error closing server socket: {e}")

            # Destroy the GUI root window
            self.gui.root.destroy()
            exit(0)

class ServerGUI:
    def __init__(self, master):
        self.root = master
        self.root.title("Chat Server")
        self.root.geometry("700x500")
        self.root.resizable(0, 0)
        self.initialize_gui()

    def initialize_gui(self):
        self.bg_image = Image.open("background2.png")
        self.bg_image = self.bg_image.resize((800, 800))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)
        frame = Frame(self.root)
        frame.pack(pady=20)
        self.root.iconbitmap('123.ico')
        self.room_list = Text(frame, width=60, height=10, font=("Serif", 12))
        self.room_list.pack(side='left', padx=10)
            
        scrollbar = Scrollbar(frame, command=self.room_list.yview, orient=VERTICAL)
        self.room_list.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.update_button = Button(self.root, text="Update Room List", command=self.update_room_list_button)
        self.update_button.pack(pady=10)

        self.clock_label = Label(self.root, text="", font=("Helvetica", 12))
        self.clock_label.pack(pady=10)
        self.update_clock()

        self.display_logos()

    def display_logos(self):
        # Load and display the logos
        try:
            # Load and display bk.png on the left
            logo_image_bk = Image.open("bk.png")
            logo_image_bk = logo_image_bk.resize((70, 70))
            logo_photo_bk = ImageTk.PhotoImage(logo_image_bk)

            logo_label_bk = Label(self.root, image=logo_photo_bk)
            logo_label_bk.image = logo_photo_bk  # Keep a reference to the image to prevent garbage collection
            logo_label_bk.place(x=250, y=400)

            # Load and display 123.ico on the right
            logo_image_123 = Image.open("123.ico")
            logo_image_123 = logo_image_123.resize((70, 70))
            logo_photo_123 = ImageTk.PhotoImage(logo_image_123)

            logo_label_123 = Label(self.root, image=logo_photo_123)
            logo_label_123.image = logo_photo_123  # Keep a reference to the image to prevent garbage collection
            logo_label_123.place(x=380, y=400)

        except Exception as e:
            messagebox.showerror("Error", f"Unable to load logo image: {e}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d"+ " | " "%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def update_room_list_button(self):
        self.update_room_list(self.rooms)

    def update_room_list(self, rooms):
        self.room_list.delete(1.0, END)
        for room_name, clients in rooms.items():
            self.room_list.insert(END, f"Room: {room_name} - {len(clients)} clients\n")
            for i, client in enumerate(clients, start=1):
                self.room_list.insert(END, f"  Client {i}: {client.getpeername()}\n")
        self.room_list.yview(END)


if __name__ == "__main__":
    root = Tk()
    gui = ServerGUI(root)
    server = ChatServer(gui)
    root.protocol("WM_DELETE_WINDOW", server.on_close_window)
    root.mainloop()