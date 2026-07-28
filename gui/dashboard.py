import csv
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.db import (
    get_last_log,
    get_all_logs,
    get_average_focus,
    get_average_sleep,
    get_average_exercise,
    get_total_study,
    get_total_logs,
    get_current_streak,
    get_settings,
    update_settings,
    change_password,
    reset_user_data,
    get_user_age,
)

from ai.ai_coach import generate_feedback
from ai.daily_challenge import get_challenge
from ai.focus_age import get_focus_age
from ai.future_self import predict_future
from ai.producticity_animal import get_animal
from ai.achievements import check_and_award_achievements

from gui.log_entry import LogEntryWindow
from gui.widgets import ModernEntry, PrimaryButton


# ---------------- Theme ---------------- #

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Dashboard(ctk.CTk):

    def __init__(self, username):

        super().__init__()

        self.username = username

        settings = get_settings(username)
        ctk.set_appearance_mode("dark" if settings["dark_mode"] else "light")

        # ---------------- Window ---------------- #

        self.title("NeuroTrack AI")
        self.geometry("1550x900")
        self.minsize(1450, 850)

        self.configure(fg_color="#0f172a")

        # ---------------- Grid ---------------- #

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =====================================================
        # Sidebar
        # =====================================================

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color="#111827"
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.sidebar.grid_propagate(False)

        # ---------------- Logo ---------------- #

        logo = ctk.CTkLabel(
            self.sidebar,
            text="🧠 NeuroTrack AI",
            font=("Arial", 28, "bold"),
            text_color="white"
        )

        logo.pack(pady=(35, 45))

        # ---------------- Buttons ---------------- #

        menu = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📈 Analytics", self.show_analytics),
            ("🤖 AI Coach", self.show_ai_coach),
            ("📅 History", self.show_history),
            ("🏆 Achievements", self.show_achievements),
            ("👤 Profile", self.show_profile),
            ("⚙ Settings", self.show_settings)
        ]

        for text, command in menu:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=48,
                width=210,
                corner_radius=12,
                font=("Arial", 16, "bold")
            )
            btn.pack(pady=8)

        # ---------------- Logout ---------------- #

        self.logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=48,
            width=210,
            corner_radius=12,
            font=("Arial", 16, "bold"),
            command=self.destroy
        )

        self.logout_btn.pack(
            side="bottom",
            pady=30
        )

        # =====================================================
        # Main Content
        # =====================================================

        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self.content.grid_columnconfigure((0, 1), weight=1)

        # =====================================================
        # Header
        # =====================================================

        self.header = ctk.CTkFrame(
            self.content,
            height=75,
            corner_radius=18
        )

        self.header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 20)
        )

        self.header.grid_columnconfigure(0, weight=1)

        self.welcome = ctk.CTkLabel(
            self.header,
            text=f"Welcome, {self.username} 👋",
            font=("Arial", 28, "bold")
        )

        self.welcome.grid(
            row=0,
            column=0,
            padx=25,
            pady=20,
            sticky="w"
        )

        # ---------------- Right Header ---------------- #

        right = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        right.grid(
            row=0,
            column=1,
            padx=20
        )

        self.log_btn = ctk.CTkButton(
            right,
            text="➕ Log Today",
            width=140,
            height=38,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.open_log_entry
        )
        self.log_btn.pack(side="left", padx=(0, 20))

        time_frame = ctk.CTkFrame(right, fg_color="transparent")
        time_frame.pack(side="left")

        self.time_label = ctk.CTkLabel(
            time_frame,
            text="",
            font=("Arial", 15)
        )

        self.time_label.pack()

        self.profile = ctk.CTkLabel(
            time_frame,
            text="🔔     👤",
            font=("Arial", 22)
        )

        self.profile.pack(pady=5)

        self.update_time()

        # =====================================================
        # Initial Dashboard View
        # =====================================================

        self.show_dashboard()

    # =====================================================
    # Log Entry Popup
    # =====================================================

    def open_log_entry(self):
        LogEntryWindow(self, self.username, on_saved=self.refresh_current_view)

    def refresh_current_view(self):
        """Re-render whichever page is currently open, so new data shows up."""
        self.current_refresh() if hasattr(self, "current_refresh") else self.show_dashboard()

    # =====================================================
    # Modern Analytics Card
    # =====================================================

    def create_card(
        self,
        row,
        column,
        title,
        value,
        icon,
        progress=0.0,
        trend="+0%"
    ):

        card = ctk.CTkFrame(
            self.content,
            corner_radius=18,
            height=170,
            fg_color="#1e293b"
        )

        card.grid(
            row=row,
            column=column,
            padx=12,
            pady=12,
            sticky="nsew"
        )

        card.grid_propagate(False)

        # ---------------- Icon ---------------- #

        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 32)
        )

        icon_label.pack(
            anchor="w",
            padx=18,
            pady=(15, 5)
        )

        # ---------------- Title ---------------- #

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 16)
        )

        title_label.pack(
            anchor="w",
            padx=18
        )

        # ---------------- Value ---------------- #

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 30, "bold")
        )

        value_label.pack(
            anchor="w",
            padx=18
        )

        # ---------------- Progress ---------------- #

        bar = ctk.CTkProgressBar(card)

        bar.pack(
            fill="x",
            padx=18,
            pady=(12, 8)
        )

        bar.set(max(0.0, min(1.0, progress)))

        # ---------------- Trend ---------------- #

        trend_label = ctk.CTkLabel(
            card,
            text=f"📈 {trend}",
            font=("Arial", 14)
        )

        trend_label.pack(
            anchor="e",
            padx=18
        )

        return card

    # =====================================================
    # Big Card (AI Coach / Today's Challenge)
    # =====================================================

    def create_big_card(
        self,
        row,
        column,
        title,
        lines,
        icon
    ):

        card = ctk.CTkFrame(
            self.content,
            corner_radius=18,
            fg_color="#1e293b",
            height=230
        )

        card.grid(
            row=row,
            column=column,
            padx=12,
            pady=12,
            sticky="nsew"
        )

        card.grid_propagate(False)

        # ---------------- Icon ---------------- #

        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 34)
        )

        icon_label.pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        # ---------------- Title ---------------- #

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 22, "bold")
        )

        title_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        # ---------------- Content ---------------- #

        for line in lines:

            lbl = ctk.CTkLabel(
                card,
                text="✔ " + line,
                font=("Arial", 15),
                anchor="w",
                justify="left",
                wraplength=430
            )

            lbl.pack(
                anchor="w",
                padx=20,
                pady=4
            )

        return card

    # =====================================================
    # Live Clock
    # =====================================================

    def update_time(self):

        current = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")

        self.time_label.configure(text=current)

        self.after(1000, self.update_time)

    # =====================================================
    # Navigation
    # =====================================================

    def clear_content(self):

        for widget in self.content.winfo_children():

            if widget != self.header:
                widget.destroy()

    # =====================================================
    # Dashboard (Home)
    # =====================================================

    def show_dashboard(self):

        self.current_refresh = self.show_dashboard

        self.clear_content()

        last_log = get_last_log(self.username)

        if last_log is None:

            empty = ctk.CTkFrame(
                self.content,
                corner_radius=18,
                fg_color="#1e293b"
            )
            empty.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=12, pady=40)

            ctk.CTkLabel(
                empty,
                text="👋 No data logged yet!",
                font=("Arial", 26, "bold")
            ).pack(pady=(40, 10))

            ctk.CTkLabel(
                empty,
                text="Click '➕ Log Today' above to add your first daily entry.",
                font=("Arial", 16)
            ).pack(pady=(0, 40))

            return

        study, sleep, exercise, scroll, mood, focus_score, log_date = last_log
        avg_focus = get_average_focus(self.username)

        self.create_card(
            1, 0,
            "Focus Score",
            f"{focus_score}%",
            "🎯",
            focus_score / 100,
            f"{focus_score - avg_focus:+.0f} vs avg"
        )

        self.create_card(
            1, 1,
            "Study Hours",
            f"{study} Hrs",
            "📚",
            min(study / 8, 1.0),
            f"Mood: {mood}"
        )

        self.create_card(
            2, 0,
            "Sleep",
            f"{sleep} Hrs",
            "😴",
            min(sleep / 9, 1.0),
            "Last night"
        )

        self.create_card(
            2, 1,
            "Exercise",
            f"{exercise} Hrs",
            "🏃",
            min(exercise / 2, 1.0),
            "Today"
        )

        feedback = generate_feedback(study, scroll, sleep)
        challenge = get_challenge()

        self.create_big_card(
            3,
            0,
            "AI Coach",
            [feedback],
            "🤖"
        )

        self.create_big_card(
            3,
            1,
            "Today's Challenge",
            [challenge],
            "🎯"
        )

    # =====================================================
    # Analytics
    # =====================================================

    def show_analytics(self):

        self.current_refresh = self.show_analytics

        self.clear_content()

        title = ctk.CTkLabel(
            self.content,
            text="📈 Analytics Dashboard",
            font=("Arial", 30, "bold")
        )
        title.grid(row=1, column=0, columnspan=2, pady=(20, 30))

        logs = get_all_logs(self.username)

        if not logs:
            ctk.CTkLabel(
                self.content,
                text="No data yet. Log a few days to see your analytics!",
                font=("Arial", 18)
            ).grid(row=2, column=0, columnspan=2, pady=40)
            return

        avg_focus = get_average_focus(self.username)
        total_study = get_total_study(self.username)
        avg_sleep = get_average_sleep(self.username)
        avg_exercise = get_average_exercise(self.username)

        self.create_card(2, 0, "Average Focus", f"{avg_focus}%", "🎯", avg_focus / 100, "overall")
        self.create_card(2, 1, "Total Study", f"{total_study} Hrs", "📚", min(total_study / 100, 1.0), "all time")
        self.create_card(3, 0, "Average Sleep", f"{avg_sleep} Hrs", "😴", min(avg_sleep / 9, 1.0), "overall")
        self.create_card(3, 1, "Average Exercise", f"{avg_exercise} Hrs", "🏃", min(avg_exercise / 2, 1.0), "overall")

        # ---------------- Chart ---------------- #

        graph = ctk.CTkFrame(
            self.content,
            corner_radius=18,
            height=320,
            fg_color="#1e293b"
        )

        graph.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=20
        )

        graph.grid_propagate(False)

        # Take the last 7 logs, oldest to newest, for a trend line
        recent = list(reversed(logs[:7]))

        dates = [row[6].split(" ")[0][5:] for row in recent]  # MM-DD
        focus_scores = [row[5] for row in recent]
        study_hours = [row[0] for row in recent]

        fig = Figure(figsize=(11, 3.4), dpi=100)
        fig.patch.set_facecolor("#1e293b")

        ax1 = fig.add_subplot(111)
        ax1.set_facecolor("#1e293b")

        ax1.bar(dates, study_hours, color="#3b82f6", alpha=0.5, label="Study Hours")
        ax1.set_ylabel("Study Hours", color="white")
        ax1.tick_params(colors="white")

        ax2 = ax1.twinx()
        ax2.plot(dates, focus_scores, color="#22c55e", marker="o", linewidth=2, label="Focus Score")
        ax2.set_ylabel("Focus Score", color="white")
        ax2.tick_params(colors="white")

        for spine in list(ax1.spines.values()) + list(ax2.spines.values()):
            spine.set_color("#334155")

        fig.suptitle("Study Hours vs Focus Score (Last 7 Logs)", color="white", fontsize=12)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # =====================================================
    # AI Coach
    # =====================================================

    def show_ai_coach(self):

        self.current_refresh = self.show_ai_coach

        self.clear_content()

        label = ctk.CTkLabel(
            self.content,
            text="🤖 AI Coach",
            font=("Arial", 30, "bold")
        )
        label.grid(row=1, column=0, columnspan=2, padx=30, pady=(20, 30))

        last_log = get_last_log(self.username)

        if last_log is None:
            ctk.CTkLabel(
                self.content,
                text="Log today's data first to get personalized AI coaching!",
                font=("Arial", 18)
            ).grid(row=2, column=0, columnspan=2, pady=40)
            return

        study, sleep, exercise, scroll, mood, focus_score, log_date = last_log
        age = get_user_age(self.username)

        feedback = generate_feedback(study, scroll, sleep)
        animal = get_animal(study, scroll, sleep)
        focus_age = get_focus_age(focus_score, age)
        future_level, success_chance = predict_future(focus_score)
        challenge = get_challenge()

        self.create_big_card(
            2, 0,
            "Personalized Feedback",
            [feedback],
            "🧠"
        )

        self.create_big_card(
            2, 1,
            "Today's Challenge",
            [challenge],
            "🎯"
        )

        self.create_big_card(
            3, 0,
            "Productivity Animal",
            [f"You're behaving like a {animal} lately!"],
            "🐾"
        )

        self.create_big_card(
            3, 1,
            "Focus Age & Future",
            [
                f"Your Focus Age is {focus_age} (real age: {age})",
                f"Predicted Level: {future_level}",
                f"Success Chance: {success_chance}"
            ],
            "🔮"
        )

    # =====================================================
    # History
    # =====================================================

    def show_history(self):

        self.current_refresh = self.show_history

        self.clear_content()

        title = ctk.CTkLabel(
            self.content,
            text="📅 Study History",
            font=("Arial", 30, "bold")
        )
        title.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=(20, 10)
        )

        logs = get_all_logs(self.username)

        # ---------------- Search + Export bar ---------------- #

        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search by date or mood...",
            width=300,
            height=38
        )
        self.search_entry.grid(row=0, column=0, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_history_table(logs))

        export_btn = ctk.CTkButton(
            toolbar,
            text="📥 Export CSV",
            width=150,
            height=38,
            command=lambda: self._export_history_csv(logs)
        )
        export_btn.grid(row=0, column=1, sticky="e")

        self.history_frame = ctk.CTkFrame(
            self.content,
            corner_radius=18,
            fg_color="#1e293b"
        )

        self.history_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=12,
            pady=10
        )

        self._render_history_table(logs)

    def _render_history_table(self, logs):

        for widget in self.history_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""

        headers = ["Date", "Study", "Sleep", "Exercise", "Scroll", "Mood", "Focus"]

        for col, head in enumerate(headers):
            ctk.CTkLabel(
                self.history_frame,
                text=head,
                font=("Arial", 16, "bold")
            ).grid(row=0, column=col, padx=20, pady=15)

        if not logs:
            ctk.CTkLabel(
                self.history_frame,
                text="No logs yet. Click '➕ Log Today' to get started!",
                font=("Arial", 16)
            ).grid(row=1, column=0, columnspan=len(headers), pady=20)
            return

        row_num = 1

        for study, sleep, exercise, scroll, mood, focus_score, log_date in logs:

            date_str = log_date.split(" ")[0]

            if query and query not in date_str.lower() and query not in mood.lower():
                continue

            values = [date_str, f"{study}h", f"{sleep}h", f"{exercise}h", f"{scroll}h", mood, str(focus_score)]

            for col, value in enumerate(values):
                ctk.CTkLabel(
                    self.history_frame,
                    text=value,
                    font=("Arial", 15)
                ).grid(row=row_num, column=col, padx=20, pady=10)

            row_num += 1

        if row_num == 1:
            ctk.CTkLabel(
                self.history_frame,
                text="No logs match your search.",
                font=("Arial", 15)
            ).grid(row=1, column=0, columnspan=len(headers), pady=20)

    def _export_history_csv(self, logs):

        if not logs:
            messagebox.showinfo("Export", "No data to export yet.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{self.username}_history.csv"
        )

        if not path:
            return

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Study", "Sleep", "Exercise", "Scroll", "Mood", "Focus Score"])

            for study, sleep, exercise, scroll, mood, focus_score, log_date in logs:
                writer.writerow([log_date, study, sleep, exercise, scroll, mood, focus_score])

        messagebox.showinfo("Export Complete", f"History exported to:\n{path}")

    # =====================================================
    # Achievements
    # =====================================================

    def show_achievements(self):

        self.current_refresh = self.show_achievements

        self.clear_content()

        label = ctk.CTkLabel(
            self.content,
            text="🏆 Achievements",
            font=("Arial", 30, "bold")
        )
        label.grid(row=1, column=0, columnspan=2, padx=30, pady=(20, 30))

        badges = check_and_award_achievements(self.username)

        row, col = 2, 0

        for badge in badges:

            card = ctk.CTkFrame(
                self.content,
                corner_radius=18,
                height=140,
                fg_color="#1e293b" if badge["earned"] else "#0f172a",
                border_width=2,
                border_color="#22c55e" if badge["earned"] else "#334155"
            )
            card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            card.grid_propagate(False)

            icon_text = badge["icon"] if badge["earned"] else "🔒"

            ctk.CTkLabel(card, text=icon_text, font=("Arial", 32)).pack(pady=(15, 5))
            ctk.CTkLabel(
                card,
                text=badge["name"],
                font=("Arial", 16, "bold"),
                text_color="white" if badge["earned"] else "#64748b"
            ).pack()
            ctk.CTkLabel(
                card,
                text=badge["description"],
                font=("Arial", 12),
                text_color="#94a3b8" if badge["earned"] else "#475569",
                wraplength=200
            ).pack(pady=(4, 10))

            col += 1
            if col > 1:
                col = 0
                row += 1

    # =====================================================
    # Profile
    # =====================================================

    def show_profile(self):

        self.current_refresh = self.show_profile

        self.clear_content()

        label = ctk.CTkLabel(
            self.content,
            text="👤 Profile",
            font=("Arial", 30, "bold")
        )
        label.grid(row=1, column=0, columnspan=2, padx=30, pady=(20, 30))

        total_study = get_total_study(self.username)
        avg_focus = get_average_focus(self.username)
        total_logs = get_total_logs(self.username)
        streak = get_current_streak(self.username)
        age = get_user_age(self.username)

        info_card = ctk.CTkFrame(self.content, corner_radius=18, fg_color="#1e293b")
        info_card.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=10)

        ctk.CTkLabel(
            info_card,
            text=f"👤 {self.username}   |   🎂 Age: {age}",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        self.create_card(3, 0, "Total Study Hours", f"{total_study} Hrs", "📚", min(total_study / 100, 1.0), "all time")
        self.create_card(3, 1, "Average Focus", f"{avg_focus}%", "🎯", avg_focus / 100, "all time")
        self.create_card(4, 0, "Total Logs", f"{total_logs}", "📅", min(total_logs / 30, 1.0), "days tracked")
        self.create_card(4, 1, "Current Streak", f"{streak} Days", "🔥", min(streak / 7, 1.0), "keep it up!")

    # =====================================================
    # Settings
    # =====================================================

    def show_settings(self):

        self.current_refresh = self.show_settings

        self.clear_content()

        label = ctk.CTkLabel(
            self.content,
            text="⚙ Settings",
            font=("Arial", 30, "bold")
        )
        label.grid(row=1, column=0, columnspan=2, padx=30, pady=(20, 30))

        settings = get_settings(self.username)

        settings_card = ctk.CTkFrame(self.content, corner_radius=18, fg_color="#1e293b")
        settings_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=12, pady=10)

        # ---------------- Dark Mode ---------------- #

        self.dark_mode_var = ctk.BooleanVar(value=settings["dark_mode"])

        dark_switch = ctk.CTkSwitch(
            settings_card,
            text="🌙 Dark Mode",
            font=("Arial", 16),
            variable=self.dark_mode_var,
            command=self._toggle_dark_mode
        )
        dark_switch.pack(anchor="w", padx=25, pady=(25, 15))

        # ---------------- Notifications ---------------- #

        self.notif_var = ctk.BooleanVar(value=settings["notifications"])

        notif_switch = ctk.CTkSwitch(
            settings_card,
            text="🔔 Notifications",
            font=("Arial", 16),
            variable=self.notif_var,
            command=self._toggle_notifications
        )
        notif_switch.pack(anchor="w", padx=25, pady=15)

        divider = ctk.CTkFrame(settings_card, height=2, fg_color="#334155")
        divider.pack(fill="x", padx=25, pady=20)

        # ---------------- Change Password ---------------- #

        ctk.CTkLabel(
            settings_card,
            text="Change Password",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=25, pady=(0, 8))

        pw_row = ctk.CTkFrame(settings_card, fg_color="transparent")
        pw_row.pack(anchor="w", padx=25, pady=(0, 20))

        self.new_password_entry = ctk.CTkEntry(
            pw_row, placeholder_text="New password", show="*", width=250, height=38
        )
        self.new_password_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            pw_row, text="Update", width=100, height=38,
            command=self._change_password
        ).pack(side="left")

        divider2 = ctk.CTkFrame(settings_card, height=2, fg_color="#334155")
        divider2.pack(fill="x", padx=25, pady=10)

        # ---------------- Danger Zone ---------------- #

        ctk.CTkLabel(
            settings_card,
            text="Danger Zone",
            font=("Arial", 16, "bold"),
            text_color="#f87171"
        ).pack(anchor="w", padx=25, pady=(10, 8))

        danger_row = ctk.CTkFrame(settings_card, fg_color="transparent")
        danger_row.pack(anchor="w", padx=25, pady=(0, 25))

        ctk.CTkButton(
            danger_row,
            text="🗑 Reset All Data",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            width=180,
            height=38,
            command=self._reset_data
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            danger_row,
            text="🚪 Logout",
            width=180,
            height=38,
            command=self.destroy
        ).pack(side="left")

    def _toggle_dark_mode(self):

        is_dark = self.dark_mode_var.get()
        update_settings(self.username, dark_mode=is_dark)
        ctk.set_appearance_mode("dark" if is_dark else "light")

    def _toggle_notifications(self):

        update_settings(self.username, notifications=self.notif_var.get())

    def _change_password(self):

        new_password = self.new_password_entry.get().strip()

        if len(new_password) < 6:
            messagebox.showerror("Weak Password", "Password must be at least 6 characters.")
            return

        change_password(self.username, new_password)
        self.new_password_entry.delete(0, "end")
        messagebox.showinfo("Success", "Password updated successfully.")

    def _reset_data(self):

        confirm = messagebox.askyesno(
            "Are you sure?",
            "This will permanently delete all your logs and achievements. Continue?"
        )

        if confirm:
            reset_user_data(self.username)
            messagebox.showinfo("Data Reset", "All your data has been cleared.")
            self.show_dashboard()


# =====================================================
# Test Dashboard
# =====================================================

if __name__ == "__main__":

    app = Dashboard("Rehan")
    app.mainloop()
