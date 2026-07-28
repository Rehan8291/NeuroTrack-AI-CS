from gui.signup import SignupWindow
from gui.dashboard import Dashboard

import customtkinter as ctk
from tkinter import messagebox

from database.auth import login
from database.db import create_tables
from gui.widgets import PrimaryButton, SecondaryButton, ModernEntry

# Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):

    def login_user(self):

        username = self.username.get().strip()
        password = self.password.get()

        if username == "":
            messagebox.showerror(
                "Error",
                "Please enter username."
            )
            return

        if password == "":
            messagebox.showerror(
                "Error",
                "Please enter password."
            )
            return

        user = login(username, password)

        if user:

            messagebox.showinfo(
                "Login Successful",
                f"Welcome back, {username}!"
            )

            self.withdraw()

            dashboard = Dashboard(username)
            dashboard.mainloop()

            self.destroy()

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid Username or Password."
            )

    def toggle_password(self):

        if self.show_password:

            self.password.configure(show="*")
            self.toggle_btn.configure(text="👁 Show Password")

        else:

            self.password.configure(show="")
            self.toggle_btn.configure(text="🙈 Hide Password")

        self.show_password = not self.show_password

    def open_signup(self):

        SignupWindow(self)

    def __init__(self):

        super().__init__()

        create_tables()

        self.title("NeuroTrack AI")
        self.geometry("1100x650")
        self.resizable(False, False)

        # ================= LEFT PANEL =================

        left_frame = ctk.CTkFrame(
            self,
            width=450,
            corner_radius=0
        )
        left_frame.pack(side="left", fill="both")

        logo = ctk.CTkLabel(
            left_frame,
            text="🧠",
            font=("Arial", 80)
        )
        logo.pack(pady=(120, 20))

        title = ctk.CTkLabel(
            left_frame,
            text="NeuroTrack AI",
            font=("SF Pro Display", 34, "bold")
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            left_frame,
            text="Track • Analyze • Improve",
            font=("Arial", 16)
        )
        subtitle.pack(pady=10)

        # ================= RIGHT PANEL =================

        right_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        right_frame.pack(side="right", expand=True)

        heading = ctk.CTkLabel(
            right_frame,
            text="Welcome Back 👋",
            font=("SF Pro Display", 32, "bold")
        )
        heading.pack(pady=(120, 35))

        self.username = ModernEntry(
            right_frame,
            "Username"
        )
        self.username.pack(pady=10)

        self.password = ModernEntry(
            right_frame,
            "Password",
            password=True
        )
        self.password.pack(pady=10)

        self.username.bind("<Return>", lambda e: self.login_user())
        self.password.bind("<Return>", lambda e: self.login_user())

        # ================= SHOW PASSWORD =================

        self.show_password = False

        self.toggle_btn = ctk.CTkButton(
            right_frame,
            text="👁 Show Password",
            width=320,
            height=35,
            fg_color="transparent",
            hover=False,
            command=self.toggle_password
        )
        self.toggle_btn.pack(pady=(5, 15))

        # ================= LOGIN BUTTON =================

        login_btn = PrimaryButton(
            right_frame,
            "LOGIN",
            self.login_user
        )
        login_btn.pack(pady=20)

        # ================= SIGNUP BUTTON =================

        signup_btn = SecondaryButton(
            right_frame,
            "Create New Account",
            self.open_signup
        )
        signup_btn.pack(pady=10)

        # Focus on username field
        self.username.focus()