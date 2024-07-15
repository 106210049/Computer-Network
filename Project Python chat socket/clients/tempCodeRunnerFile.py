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