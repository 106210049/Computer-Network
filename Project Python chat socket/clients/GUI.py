import socket
import threading
from tkinter import Tk, Frame, Scrollbar, Label, END, Text, VERTICAL, Button, messagebox
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

FORMAT = 'utf-8'
# Connection
PORT = 10319
IP_ADDR = '127.0.0.1'


class GUI:
    client_socket = None
    last_received_message = None
    client_count_label = None
    last_displayed_date = None

    def __init__(self, master, full_name, room_name):
        self.root = master
        self.full_name = full_name
        self.room_name = room_name

        self.chat_transcript_area = None
        self.enter_text_widget = None

        self.chat_log_file = open(f"{room_name}_chat_log.txt", "a+")
        self.chat_log_file.seek(0)
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
        self.bg_image = self.bg_image.resize((800, 800))
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
                join_message = user + " has joined"
                self.display_message_with_timestamp(join_message, tag="join")
                self.save_message_to_log(join_message)
            else:
                self.display_message_with_timestamp(message, tag="message")
                self.save_message_to_log(message)

        so.close()

    def display_message_with_timestamp(self, message, tag="message"):
        current_time = datetime.now()
        timestamp = current_time.strftime('%H:%M:%S')
        current_date = current_time.strftime('%Y-%m-%d')

        if self.last_displayed_date != current_date:
            self.last_displayed_date = current_date
            date_message = f"----- {current_date} -----"
            self.chat_transcript_area.insert('end', date_message + '\n', "date")
            self.save_message_to_log(date_message)

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
            self.display_message_with_timestamp(self.full_name + ": " + data, tag="self")
            self.save_message_to_log(self.full_name + ": " + data)
            self.enter_text_widget.delete(1.0, 'end')

    def save_message_to_log(self, message):
        self.chat_log_file.write(message + '\n')
        self.chat_log_file.flush()

    def load_chat_history(self):
        self.chat_transcript_area.delete(1.0, END)  # Clear previous messages
        last_date = None
        for line in self.chat_log_file:
            if line.startswith("-----"):
                last_date = line.strip("----- \n")
                self.chat_transcript_area.insert(END, line, "date")
            else:
                self.chat_transcript_area.insert(END, line, "message")
        self.last_displayed_date = last_date
        self.chat_transcript_area.yview(END)

    def delete_messages(self):
        self.chat_transcript_area.delete(1.0, END)
        self.chat_log_file.close()
        self.chat_log_file = open(f"{self.room_name}_chat_log.txt", "w")
        self.chat_log_file.close()
        self.chat_log_file = open(f"{self.room_name}_chat_log.txt", "a+")
        self.chat_log_file.seek(0)

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.client_socket:
                try:
                    self.client_socket.send(("left:" + self.full_name).encode(FORMAT))
                except Exception as e:
                    print(f"Error sending leave message: {e}")
                finally:
                    self.client_socket.close()
            self.chat_log_file.close()
            self.root.destroy()
            exit(0)


# if __name__ == "__main__":
#     root = Tk()
#     full_name = "Your Name"
#     room_name = "Room1"
#     gui = GUI(root, full_name, room_name)
#     root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
#     root.mainloop()
