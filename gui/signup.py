import customtkinter as ctk
from tkinter import messagebox

from database.auth import signup
from gui.widgets import PrimaryButton, ModernEntry


class SignupWindow(ctk.CTkToplevel):

    def create_account(self):

        username = self.username.get().strip()
        password = self.password.get()
        confirm = self.confirm.get()
        age_text = self.age.get().strip()

        if username == "" or password == "" or confirm == "":
            messagebox.showerror(
                "Error",
                "Please fill all fields."
            )
            return

        if len(username) < 3:
            messagebox.showerror(
                "Invalid Username",
                "Username must contain at least 3 characters."
            )
            return

        if len(password) < 6:
            messagebox.showerror(
                "Weak Password",
                "Password must contain at least 6 characters."
            )
            return

        if password != confirm:
            messagebox.showerror(
                "Error",
                "Passwords do not match."
            )
            return

        if age_text == "":
            age = 18
        else:
            try:
                age = int(age_text)
                if age <= 0 or age > 120:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Age",
                    "Please enter a valid age (or leave it blank)."
                )
                return

        if signup(username, password, age):
            messagebox.showinfo(
                "Success",
                "Your account has been created successfully."
            )
            self.destroy()

        else:
            messagebox.showerror(
                "Error",
                "Username already exists."
            )

    def __init__(self, parent):

        super().__init__(parent)

        self.title("Create Account")
        self.geometry("500x500")
        self.resizable(False, False)

        title = ctk.CTkLabel(
            self,
            text="Create Account",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=30)

        self.username = ModernEntry(
            self,
            "Username"
        )
        self.username.pack(pady=10)

        self.password = ModernEntry(
            self,
            "Password",
            password=True
        )
        self.password.pack(pady=10)

        self.confirm = ModernEntry(
            self,
            "Confirm Password",
            password=True
        )
        self.confirm.pack(pady=10)

        self.age = ModernEntry(
            self,
            "Age (optional)"
        )
        self.age.pack(pady=10)

        create_btn = PrimaryButton(
            self,
            "Create Account",
            self.create_account
        )
        create_btn.pack(pady=25)

        self.username.bind("<Return>", lambda e: self.create_account())
        self.password.bind("<Return>", lambda e: self.create_account())
        self.confirm.bind("<Return>", lambda e: self.create_account())

        self.username.focus()