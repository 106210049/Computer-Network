from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, OptionMenu, StringVar, messagebox
from tkinter import ttk
from GUI import GUI
class LoginGUI:
    def __init__(self, master):
        self.root = master
        self.root.title("Login")
        self.root.resizable(0,0)
        self.root.geometry("500x400")
        # self.resizable(width=False, height=False)
        self.initialize_login_gui()

    def initialize_login_gui(self):
        frame = Frame(self.root)
        frame.pack(pady=10)

        frame_3 = Frame(self.root)
        frame_3.pack(pady=10)

        frame_2 = Frame(self.root)
        frame_2.pack(pady=10)

        frame_4 = Frame(self.root)
        frame_4.pack(pady=10)

        Label(frame, text='Enter your full name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_entry = Entry(frame, width=50, borderwidth=2)
        self.name_entry.pack(side='left', padx=10)

        Label(frame_3, text='Enter your password:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.password = Entry(frame_3, width=50, borderwidth=2)
        self.password.pack(side='left', padx=10)

        Label(frame_2, text='Select room:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.room_var = StringVar()
        self.room_menu = ttk.Combobox(frame_2, textvariable=self.room_var, state='readonly')
        self.room_menu['values'] = ("Room 1", "Room 2", "Room 3")
        self.room_menu.set("Room 1")  # Default value
        self.room_menu.pack(side='left', padx=10)

        Label(frame_4, text="Enter your room's password:", font=("Helvetica", 16)).pack(side='left', padx=10)
        self.password = Entry(frame_4, width=50, borderwidth=2)
        self.password.pack(side='left', padx=10)

        join_button = Button(frame_2, text="Join", width=10, command=self.on_join)
        join_button.pack(side='left', padx=60)

    def on_join(self):
        full_name = self.name_entry.get().strip()
        room_name = self.room_var.get()
        if len(full_name) == 0:
            messagebox.showerror("Enter your name", "Please enter your full name.")
            return
        self.root.destroy()
        chat_window = Tk()
        chat_gui = GUI(chat_window, full_name, room_name)
        chat_window.protocol("WM_DELETE_WINDOW", chat_gui.on_close_window)
        chat_window.mainloop()

if __name__ == '__main__':
    root = Tk()
    login_gui = LoginGUI(root)
    root.mainloop()