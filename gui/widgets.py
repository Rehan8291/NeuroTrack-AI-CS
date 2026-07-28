import customtkinter as ctk


class PrimaryButton(ctk.CTkButton):

    def __init__(self, master, text, command):

        super().__init__(
            master=master,
            text=text,
            command=command,
            width=320,
            height=45,
            corner_radius=12,
            font=("Arial", 15, "bold")
        )


class SecondaryButton(ctk.CTkButton):

    def __init__(self, master, text, command):

        super().__init__(
            master=master,
            text=text,
            command=command,
            width=320,
            height=45,
            corner_radius=12,
            fg_color="transparent",
            border_width=2,
            font=("Arial", 15)
        )


class ModernEntry(ctk.CTkEntry):

    def __init__(self, master, placeholder, password=False):

        super().__init__(
            master=master,
            width=320,
            height=45,
            corner_radius=12,
            placeholder_text=placeholder
        )

        if password:
            self.configure(show="*")