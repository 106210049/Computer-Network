
        join_button = Button(frame_2,text="Join", width=10, command=self.on_join)
        join_button.pack(side='left', padx=60)

        Label(frame_5, text="Register if you don't have access", font=("Helvetica", 10)).pack(side='top', padx=10)
        register_button = Button(frame_5,text="Register", width=15, command=self.Register)
        register_button.pack(side='left', padx=60)