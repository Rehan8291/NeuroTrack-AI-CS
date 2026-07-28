import customtkinter as ctk
from tkinter import messagebox

from database.db import save_log
from ai.focus_calculator import calculate_focus_score
from ai.achievements import check_and_award_achievements
from gui.widgets import ModernEntry, PrimaryButton


class LogEntryWindow(ctk.CTkToplevel):
    """
    Popup form where the user enters today's study / sleep / exercise /
    scroll hours + mood. On save, it calculates the focus score, stores
    the log, checks for new achievements, and refreshes the dashboard
    via the on_saved callback.
    """

    def __init__(self, parent, username, on_saved=None):

        super().__init__(parent)

        self.username = username
        self.on_saved = on_saved

        self.title("Log Today's Data")
        self.geometry("450x620")
        self.resizable(False, False)

        # Keep this window on top of the dashboard
        self.transient(parent)
        self.grab_set()

        title = ctk.CTkLabel(
            self,
            text="📝 Log Today's Data",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=(25, 20))

        self.study = ModernEntry(self, "Study Hours (e.g. 3.5)")
        self.study.pack(pady=8)

        self.sleep = ModernEntry(self, "Sleep Hours (e.g. 7)")
        self.sleep.pack(pady=8)

        self.exercise = ModernEntry(self, "Exercise Hours (e.g. 0.5)")
        self.exercise.pack(pady=8)

        self.scroll = ModernEntry(self, "Scroll / Phone Hours (e.g. 2)")
        self.scroll.pack(pady=8)

        mood_label = ctk.CTkLabel(self, text="Mood", font=("Arial", 14))
        mood_label.pack(pady=(15, 5))

        self.mood = ctk.CTkOptionMenu(
            self,
            values=["😄 Great", "😊 Good", "😐 Okay", "😔 Low", "😴 Tired"],
            width=320,
            height=40
        )
        self.mood.pack(pady=5)

        save_btn = PrimaryButton(self, "Save Log", self.save)
        save_btn.pack(pady=(30, 10))

        self.study.focus()

    def _parse_hours(self, entry, field_name):
        value = entry.get().strip()

        if value == "":
            value = "0"

        try:
            number = float(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a number.")

        if number < 0 or number > 24:
            raise ValueError(f"{field_name} must be between 0 and 24.")

        return number

    def save(self):

        try:
            study = self._parse_hours(self.study, "Study hours")
            sleep = self._parse_hours(self.sleep, "Sleep hours")
            exercise = self._parse_hours(self.exercise, "Exercise hours")
            scroll = self._parse_hours(self.scroll, "Scroll hours")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        mood = self.mood.get()

        focus_score = calculate_focus_score(study, sleep, exercise, scroll)

        save_log(
            self.username,
            study,
            sleep,
            exercise,
            scroll,
            mood,
            focus_score
        )

        # Check if this log unlocked any new achievements
        check_and_award_achievements(self.username)

        messagebox.showinfo(
            "Saved!",
            f"Today's log saved.\nFocus Score: {focus_score}%"
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()
