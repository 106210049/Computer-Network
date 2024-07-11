import socket
import threading
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox
from datetime import datetime  # Import datetime module for timestamp

class LoginGUI:
    def __init__(self, master):
        self.root = master
        self.root.title("Login")
        self.root.resizable(0, 0)
        self.initialize_login_gui()

    def initialize_login_gui(self):
        frame = Frame(self.root)
        frame.pack(pady=20)
        frame_2 = Frame(self.root)
        frame_2.pack(pady=20)
        Label(frame, text='Enter your full name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_entry = Entry(frame, width=50, borderwidth=2)
        self.name_entry.pack(side='left', padx=10)

        Label(frame_2, text='Select room:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.room_entry = Entry(frame_2, width=20, borderwidth=2)
        self.room_entry.pack(side='left', padx=10)

        join_button = Button(frame, text="Join", width=10, command=self.on_join)
        join_button.pack(side='left', padx=10)

    def on_join(self):
        full_name = self.name_entry.get().strip()
        if len(full_name) == 0:
            messagebox.showerror("Enter your name", "Please enter your full name.")
            return
        self.root.destroy()  # Close the login window
        chat_window = Tk()
        chat_gui = GUI(chat_window, full_name)
        chat_window.protocol("WM_DELETE_WINDOW", chat_gui.on_close_window)
        chat_window.mainloop()

class GUI:
    client_socket = None
    last_received_message = None
    client_count_label = None
    
    def __init__(self, master, full_name):
        self.root = master
        self.full_name = full_name
        self.chat_transcript_area = None
        self.enter_text_widget = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = '127.0.0.1'
        remote_port = 10319
        self.client_socket.connect((remote_ip, remote_port))

    def initialize_gui(self):
        self.root.title("Socket Chat")
        self.root.resizable(0, 0)
        self.display_chat_box()
        self.display_chat_entry_box()
        self.display_client_count()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')
            print(message)

            if message.startswith("count:"):
                self.update_client_count(message.split(":")[1])
            elif "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.display_message_with_timestamp(message)

        so.close()

    def display_message_with_timestamp(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')  # Get current time in HH:MM:SS format
        message_with_timestamp = f"[{timestamp}] {message}"
        self.chat_transcript_area.insert('end', message_with_timestamp + '\n')
        self.chat_transcript_area.yview(END)

    def display_chat_box(self):
        frame = Frame(self.root)
        frame.pack(pady=20)

        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        self.chat_transcript_area.pack(side='top', padx=10)

        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def display_chat_entry_box(self):
        frame = Frame(self.root)
        frame.pack(pady=20)

        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='left', padx=10)
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', padx=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)

        send_button = Button(frame, text="Send", width=10, command=self.send_chat)
        send_button.pack(side='left', padx=10)

    def display_client_count(self):
        frame = Frame(self.root)
        frame.pack(pady=10)
        
        Label(frame, text='Number of clients:', font=("Helvetica", 14)).pack(side='left', padx=10)
        self.client_count_label = Label(frame, text='0', font=("Helvetica", 14))
        self.client_count_label.pack(side='left', padx=10)

    def update_client_count(self, count):
        self.client_count_label.config(text=count)

    def on_enter_key_pressed(self, event):
        self.send_chat()

    def send_chat(self):
        data = self.enter_text_widget.get(1.0, 'end').strip()
        if data:
            message = (self.full_name + ": " + data).encode('utf-8')
            self.client_socket.send(message)
            self.display_message_with_timestamp(data)  # Hiển thị tin nhắn ngay khi gửi
            self.enter_text_widget.delete(1.0, 'end')

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.client_socket:
                try:
                    self.client_socket.send(("left:" + self.full_name).encode('utf-8'))
                except Exception as e:
                    print(f"Error sending leave message: {e}")
                finally:
                    self.client_socket.close()
        self.root.destroy()
        exit(0)

if __name__ == '__main__':
    root = Tk()
    login_gui = LoginGUI(root)
    root.mainloop()
