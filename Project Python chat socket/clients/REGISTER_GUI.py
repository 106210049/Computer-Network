from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, OptionMenu, StringVar, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from GUI import GUI

ROOM_PASSWORD_1='1234'
ROOM_PASSWORD_2='7890'
ROOM_PASSWORD_3='7749'

class LoginGUI:
    def __init__(self, master):
        self.root = master
        self.root.title("Login")
        self.root.resizable(0,0)
        self.root.geometry("500x400")
        self.root.iconbitmap('123.ico')
        # self.resizable(width=False, height=False)
        self.initialize_login_gui()

    def initialize_login_gui(self):

        self.bg_image = Image.open("background2.png")
        self.bg_image = self.bg_image.resize((800, 800))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        frame = Frame(self.root)
        frame.pack(pady=10)

        frame_3 = Frame(self.root)
        frame_3.pack(pady=10)

        frame_2 = Frame(self.root)
        frame_2.pack(pady=10)

        frame_4 = Frame(self.root)
        frame_4.pack(pady=10)

        frame_5 = Frame(self.root)
        frame_5.pack(pady=10)

                
        Label(frame, text='Enter your full name:', font=("Helvetica", 14), bg='#ADD8E6').pack(side='left', padx=10)
        self.name_entry = Entry(frame, width=60, borderwidth=2)
        self.name_entry.pack(side='left', padx=10)

        Label(frame_3, text='Enter your password:', font=("Helvetica", 14), bg='#ADD8E6').pack(side='left', padx=10)
        self.password = Entry(frame_3, width=60, borderwidth=2)
        self.password.pack(side='left', padx=10)

        Label(frame_2, text='Select room:', font=("Helvetica", 14), bg='#ADD8E6').pack(side='left', padx=10)
        self.room_var = StringVar()
        self.room_menu = ttk.Combobox(frame_2, textvariable=self.room_var, state='readonly')
        self.room_menu['values'] = ("Room 1", "Room 2", "Room 3")
        self.room_menu.set(" ")  # Default value
        self.room_menu.pack(side='left', padx=10)

        Label(frame_4, text="Enter your room's password:", font=("Helvetica", 14), bg='#ADD8E6').pack(side='left', padx=10)
        self.room_password = Entry(frame_4, width=60, borderwidth=2)
        self.room_password.pack(side='left', padx=10)

        join_button = Button(frame_2,text="Join", width=10, command=self.on_join)
        join_button.pack(side='left', padx=60)

        Label(frame_5, text="Register if you don't have access", font=("Helvetica", 10)).pack(side='top', padx=10)
        join_button = Button(frame_5,text="Register", width=15, command=self.Register)
        join_button.pack(side='left', padx=60)

        self.display_logo()

    def display_logo(self):
        frame = Frame(self.root)
        frame.pack(side='bottom', pady=10)

        # Load and display the logos
        try:
            # Load and display bk.png on the left
            logo_image_bk = Image.open("bk.png")
            logo_image_bk = logo_image_bk.resize((100, 100))
            logo_photo_bk = ImageTk.PhotoImage(logo_image_bk)

            logo_label_bk = Label(frame, image=logo_photo_bk)
            logo_label_bk.image = logo_photo_bk  # Keep a reference to the image to prevent garbage collection
            logo_label_bk.pack(side='left', padx=10)

            # Load and display 123.ico on the right
            logo_image_123 = Image.open("123.ico")
            logo_image_123 = logo_image_123.resize((100, 100))
            logo_photo_123 = ImageTk.PhotoImage(logo_image_123)

            logo_label_123 = Label(frame, image=logo_photo_123)
            logo_label_123.image = logo_photo_123  # Keep a reference to the image to prevent garbage collection
            logo_label_123.pack(side='right', padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Unable to load logo image: {e}")

            
        

    def on_join(self):
        full_name = self.name_entry.get().strip()
        room_name = self.room_var.get()
        private_password=self.password.get()
        room_pass=self.room_password.get()
        if len(full_name) == 0:
            messagebox.showerror("Enter your name", "Please enter your full name.")
            return
        if len(private_password) == 0:
            messagebox.showerror("Enter your password", "Please enter your password.")
            return
        if len(room_name) == 0:
            messagebox.showerror("Choose your name", "Please choose your room.")
            return
        if len(room_pass) == 0:
            messagebox.showerror("Enter your room's password", "Please enter your room's password.")
            return
        
        if room_name=='Room 1':
            if(room_pass!=ROOM_PASSWORD_1):
                messagebox.showerror("Wrong password", "Please enter room's password again.")
                return
        elif room_name=='Room 2':
            if(room_pass!=ROOM_PASSWORD_2):
                messagebox.showerror("Wrong password", "Please enter room's password again.")
                return
        else:
            if(room_pass!=ROOM_PASSWORD_3):
                messagebox.showerror("Wrong password", "Please enter room's password again.")
                return
        self.root.destroy()
        chat_window = Tk()
        chat_gui = GUI(chat_window, full_name, room_name)
        chat_window.protocol("WM_DELETE_WINDOW", chat_gui.on_close_window)
        chat_window.mainloop()
    
class REGISTER_GUI:
    def __init__(self, master):
        self.root = master
        self.root.title("Register")
        self.root.iconbitmap('123.ico')
        self.root.resizable(0,0)
        self.root.geometry("500x400")
        # self.resizable(width=False, height=False)
        self.initialize_register_gui()

    def initialize_register_gui(self):
        self.bg_image = Image.open("background2.png")
        self.bg_image = self.bg_image.resize((700, 700))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)
        frame = Frame(self.root)
        frame.pack(pady=10,padx=10)

        frame_3 = Frame(self.root)
        frame_3.pack(pady=10,padx=10)

        frame_2 = Frame(self.root)
        frame_2.pack(pady=10,padx=10)

        frame_4 = Frame(self.root)
        frame_4.pack(pady=10,padx=10)

        frame_5 = Frame(self.root)
        frame_5.pack(pady=10,padx=10)

        Label(frame, text='Enter your full name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_entry = Entry(frame, width=50, borderwidth=2)
        self.name_entry.pack(side='left', padx=10)

        Label(frame_3, text='Enter your password:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.password = Entry(frame_3, width=50, borderwidth=2)
        self.password.pack(side='left', padx=10)

        Label(frame_2, text='Select room:', font=("Helvetica", 14)).pack(side='left', padx=10)
        self.room_var = StringVar()
        self.room_menu = ttk.Combobox(frame_2, textvariable=self.room_var, state='readonly')
        self.room_menu['values'] = ("Room 1", "Room 2", "Room 3")
        self.room_menu.set(" ")  # Default value
        self.room_menu.pack(side='left', padx=10)
        
        Label(frame_4, text="Enter your room's password:", font=("Helvetica", 16)).pack(side='left', padx=10)
        self.room_password = Entry(frame_4, width=50, borderwidth=2)
        self.room_password.pack(side='left', padx=10)

        # join_button = Button(frame_2,text="Join", width=10, command=self.on_join)
        # join_button.pack(side='left', padx=60)

        register_button = Button(frame_5,text="Register", width=10, command=self.Register_Success)
        register_button.pack(side='left', padx=60)

        self.display_logo()

    def display_logo(self):
        frame = Frame(self.root)
        frame.pack(side='bottom', pady=10)

        # Load and display the logos
        try:
            # Load and display bk.png on the left
            logo_image_bk = Image.open("bk.png")
            logo_image_bk = logo_image_bk.resize((100, 100))
            logo_photo_bk = ImageTk.PhotoImage(logo_image_bk)

            logo_label_bk = Label(frame, image=logo_photo_bk)
            logo_label_bk.image = logo_photo_bk  # Keep a reference to the image to prevent garbage collection
            logo_label_bk.pack(side='left', padx=10)

            # Load and display 123.ico on the right
            logo_image_123 = Image.open("123.ico")
            logo_image_123 = logo_image_123.resize((100, 100))
            logo_photo_123 = ImageTk.PhotoImage(logo_image_123)

            logo_label_123 = Label(frame, image=logo_photo_123)
            logo_label_123.image = logo_photo_123  # Keep a reference to the image to prevent garbage collection
            logo_label_123.pack(side='right', padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Unable to load logo image: {e}")


    def Register_Success(self):
        full_name = self.name_entry.get().strip()
        private_password=self.password.get()
        room_pass=self.room_password.get()
        if len(full_name) == 0:
            messagebox.showerror("Enter your name", "Please enter your full name.")
            return
        if len(private_password) == 0:
            messagebox.showerror("Enter your password", "Please enter your password.")
            return
        
        if len(room_pass) == 0:
            messagebox.showerror("Enter your room's password", "Please enter your room's password.")
            return
        
        messagebox.showinfo("Register success", "Successful, please login to use this app")
        
        self.root.destroy()
        self.open_login_window()

    def open_login_window(self):
        root = Tk()
        login_gui = LoginGUI(root)
        root.mainloop()
    



    
        