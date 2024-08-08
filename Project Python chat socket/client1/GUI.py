import socket
import threading
from tkinter import Tk, Frame, Scrollbar, Label, END, Text, VERTICAL, Button, messagebox
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
from vidstream import CameraClient, StreamingServer
from pymongo import MongoClient

FORMAT = 'utf-8'

# Connection
PORT = 10319
IP_ADDR = '127.0.0.1'
MONGO_URI = "mongodb://localhost:27017/"

class ChatServer:
    def __init__(self, gui):
        self.server_socket = None
        self.rooms = {}  # Dictionary to store chat rooms
        self.video_call_servers = {}  # Dictionary to store video call servers per room
        self.gui = gui
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client["chat_db"]
        self.messages_collection = self.db["messages"]
        self.create_listening_server()

    def create_listening_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket using TCP port and ipv4
        local_ip = '127.0.0.1'
        local_port = 10320  # Change to a different port
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
                    self.save_message_to_db(room_name, message)
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

            # Gửi lịch sử tin nhắn cho client mới kết nối
            self.send_chat_history(client_socket, room_name)

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

    def save_message_to_db(self, room_name, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.messages_collection.insert_one({
            "room_name": room_name,
            "timestamp": timestamp,
            "message": message
        })

    def send_chat_history(self, client_socket, room_name):
        messages = self.messages_collection.find({"room_name": room_name})
        for msg in messages:
            message_with_timestamp = f"{msg['timestamp']} | {msg['message']}"
            client_socket.sendall(message_with_timestamp.encode('utf-8'))

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

            # Close MongoDB connection
            self.mongo_client.close()

            # Destroy the GUI root window
            self.gui.root.destroy()
            exit(0)

class GUI:
    client_socket = None
    last_received_message = None
    client_count_label = None
    last_displayed_date = None
    video_call_client = None
    video_call_server = None

    def __init__(self, master, full_name, room_name):
        self.root = master
        self.full_name = full_name
        self.room_name = room_name

        self.chat_transcript_area = None
        self.enter_text_widget = None

        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client["chat_db"]
        self.messages_collection = self.db["messages"]

        self.initialize_socket()
        self.initialize_gui()
        self.load_chat_history()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = IP_ADDR
        remote_port = PORT
        self.client_socket.connect((remote_ip, remote_port))
        self.client_socket.send(self.room_name.encode(FORMAT))

    def initialize_gui(self):
        self.root.title(f"Socket Chat - {self.room_name}")
        self.root.iconbitmap('123.ico')
        self.root.resizable(0, 0)

        # Load background image
        self.bg_image = Image.open("background2.png")
        self.bg_image = self.bg_image.resize((1000, 1000))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # Display logos
        self.display_logos()

        self.display_room_name()
        self.display_chat_box()
        self.display_chat_entry_box()
        self.display_client_count()
        self.display_delete_button()
        self.display_video_call_button()

    def display_logos(self):
        # Load and display the logos
        try:
            # Load and display bk.png on the left
            logo_image_bk = Image.open("bk.png")
            logo_image_bk = logo_image_bk.resize((50, 50))
            logo_photo_bk = ImageTk.PhotoImage(logo_image_bk)

            logo_label_bk = Label(self.root, image=logo_photo_bk)
            logo_label_bk.image = logo_photo_bk  # Keep a reference to the image to prevent garbage collection
            logo_label_bk.place(x=20, y=10)

            # Load and display 123.ico on the right
            logo_image_123 = Image.open("123.ico")
            logo_image_123 = logo_image_123.resize((50, 50))
            logo_photo_123 = ImageTk.PhotoImage(logo_image_123)

            logo_label_123 = Label(self.root, image=logo_photo_123)
            logo_label_123.image = logo_photo_123  # Keep a reference to the image to prevent garbage collection
            logo_label_123.place(x=100, y=10)

        except Exception as e:
            messagebox.showerror("Error", f"Unable to load logo image: {e}")

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode(FORMAT)
            print(message)

            if message.startswith("count:"):
                self.update_client_count(message.split(":")[1])
            elif "joined" in message:
                user = message.split(":")[1]
                join_message = user
                join_message = user + " has joined"
                # self.send_chat(join_message.encode(FORMAT))
                self.display_message_with_timestamp(join_message, tag="join")
                self.save_message_to_db(join_message)
            else:
                self.display_message_with_timestamp(message, tag="message")
                # self.save_message_to_db(message)

        so.close()

    def display_message_with_timestamp(self, message, tag="message"):
        current_time = datetime.now()
        timestamp = current_time.strftime('%H:%M:%S')
        current_date = current_time.strftime('%Y-%m-%d')

        if self.last_displayed_date != current_date:
            self.last_displayed_date = current_date
            date_message = f"----- {current_date} -----"
            self.chat_transcript_area.insert('end', date_message + '\n', "date")
            self.save_message_to_db(date_message)

        message_with_timestamp = f"[{timestamp}] {message}"
        self.chat_transcript_area.insert('end', message_with_timestamp + '\n', tag)
        self.chat_transcript_area.yview(END)

    def display_room_name(self):
        frame = Frame(self.root, bg='#ADD8E6')
        frame.pack(pady=10)

        Label(frame, text=f"Room: {self.room_name}", font=("Helvetica", 16), bg='#ADD8E6').pack(side='top', pady=10)

    def display_chat_box(self):
        frame = Frame(self.root, bg='#ADD8E6')
        frame.pack(pady=20)

        self.chat_transcript_area = Text(frame, width=60, height=15, font=("Serif", 12), bg='#E6E6FA')
        self.chat_transcript_area.pack(side='top', padx=10)

        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.chat_transcript_area.tag_configure("join", foreground="blue")
        self.chat_transcript_area.tag_configure("message", foreground="black")
        self.chat_transcript_area.tag_configure("date", foreground="green")
        self.chat_transcript_area.tag_configure("self", foreground="black")

    def display_chat_entry_box(self):
        frame = Frame(self.root, bg='#ADD8E6')
        frame.pack(pady=20)

        Label(frame, text='Enter message:', font=("Serif", 12), bg='#ADD8E6').pack(side='left', padx=10)
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12), bg='#E6E6FA')
        self.enter_text_widget.pack(side='left', padx=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)

        send_button = Button(frame, text="Send", width=10, command=self.send_chat)
        send_button.pack(side='left', padx=10)

    def display_delete_button(self):
        frame = Frame(self.root, bg='#ADD8E6')
        frame.pack(pady=10)

        delete_button = Button(frame, text="Delete Messages", width=20, command=self.delete_messages)
        delete_button.pack(pady=10)

    def display_client_count(self):
        frame = Frame(self.root, bg='#ADD8E6')
        frame.pack(pady=10)

        Label(frame, text='Number of clients:', font=("Helvetica", 14), bg='#ADD8E6').pack(side='left', padx=10)
        self.client_count_label = Label(frame, text='0', font=("Helvetica", 14), bg='#ADD8E6')
        self.client_count_label.pack(side='left', padx=10)

    def display_video_call_button(self):
        frame = Frame(self.root, bg='#ADD8E6')
        frame.pack(pady=10)

        video_call_button = Button(frame, text="Video Call", width=20, command=self.start_video_call)
        video_call_button.pack(pady=10)

    def update_client_count(self, count):
        self.client_count_label.config(text=count)

    def on_enter_key_pressed(self, event):
        self.send_chat()
        return 'break'  # Prevent newline being added to the text widget

    def send_chat(self):
        data = self.enter_text_widget.get(1.0, 'end').strip()
        if data:
            message = (self.full_name + ": " + data).encode(FORMAT)
            self.client_socket.send(message)
            
            # Hiển thị tin nhắn trên giao diện
            self.display_message_with_timestamp(self.full_name + ": " + data, tag="self")
            
            # Lưu tin nhắn vào log ngay lập tức
            self.save_message_to_db(self.full_name + ": " + data)
            
            self.enter_text_widget.delete(1.0, 'end')
            
    def save_message_to_db(self, message):
        # current_time = datetime.now().strftime('%H:%M:%S')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.messages_collection.insert_one({
            "room_name": self.room_name,
            "timestamp": timestamp,
            "message": message
        })

    def load_chat_history(self):
        # self.chat_transcript_area.delete(1.0, END)  # Clear previous messages
        # last_date = None
        # messages = self.messages_collection.find({"room_name": self.room_name})
        # for msg in messages:
        #     timestamp = msg["timestamp"]
        #     message = msg["message"]
        #     if timestamp.startswith("-----"):
        #         last_date = timestamp.strip("----- \n")
        #         self.chat_transcript_area.insert(END, timestamp, "date")
        #     else:
        #         self.chat_transcript_area.insert(END, f"{timestamp} | {message}\n", "message")
        # self.last_displayed_date = last_date
        # self.chat_transcript_area.yview(END)
        # Clear the chat box before loading messages to prevent duplicates
        self.chat_transcript_area.delete(1.0, END)

        messages = self.messages_collection.find({"room_name": self.room_name})
        for msg in messages:
            message_with_timestamp = f"{msg['timestamp']} | {msg['message']}\n"
            self.chat_transcript_area.insert(END, message_with_timestamp)


    def delete_messages(self):
        self.chat_transcript_area.delete(1.0, END)
        self.messages_collection.delete_many({"room_name": self.room_name})

    def start_video_call(self):
        if not self.video_call_server:
            self.video_call_server = StreamingServer(IP_ADDR, PORT + 1)
            self.video_call_server.start_server()

        if not self.video_call_client:
            self.video_call_client = CameraClient(IP_ADDR, PORT + 1)
            self.video_call_client.start_stream()

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.client_socket:
                try:
                    self.client_socket.send(("left:" + self.full_name).encode(FORMAT))
                except Exception as e:
                    print(f"Error sending leave message: {e}")
                finally:
                    self.client_socket.close()
            self.mongo_client.close()
            if self.video_call_client:
                self.video_call_client.stop_stream()
            if self.video_call_server:
                self.video_call_server.stop_server()
            self.root.destroy()
            exit(0)

