import sqlite3
import os

# Always resolve the db path relative to this file, so it works
# no matter where main.py is run from.
DB_NAME = os.path.join(os.path.dirname(__file__), "neurotrack.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- USERS ---------------- #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Older databases won't have the "age" column yet (needed for the
    # Focus Age AI feature). Add it if it's missing, default to 18.
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 18")
    except sqlite3.OperationalError:
        pass  # column already exists

    # ---------------- USER LOGS ---------------- #

    # Older prototype versions of this app (the CLI version) created
    # user_logs with a different schema: (name, age, study, scroll,
    # sleep, exercise, mood, focus_score) - no "username" or "log_date"
    # column. If that old table is still sitting in the .db file, the
    # GUI's save_log()/get_all_logs() calls below would crash. Detect
    # that case and safely rename the old table out of the way first,
    # instead of losing data or crashing.

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='user_logs'
    """)

    if cursor.fetchone():

        cursor.execute("PRAGMA table_info(user_logs)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        if "username" not in existing_columns or "log_date" not in existing_columns:

            backup_name = "user_logs_legacy_backup"
            suffix = 1

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = {row[0] for row in cursor.fetchall()}

            while backup_name in all_tables:
                suffix += 1
                backup_name = f"user_logs_legacy_backup_{suffix}"

            cursor.execute(f"ALTER TABLE user_logs RENAME TO {backup_name}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        study REAL,
        sleep REAL,
        exercise REAL,
        scroll REAL,

        mood TEXT,

        focus_score INTEGER,

        log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- ACHIEVEMENTS ---------------- #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        badge_name TEXT,

        earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- SETTINGS ---------------- #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        dark_mode INTEGER DEFAULT 1,

        notifications INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


# ---------------- SAVE DAILY LOG ---------------- #

def save_log(username, study, sleep, exercise, scroll, mood, score):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO user_logs(
        username,
        study,
        sleep,
        exercise,
        scroll,
        mood,
        focus_score
    )
    VALUES(?,?,?,?,?,?,?)
    """, (
        username,
        study,
        sleep,
        exercise,
        scroll,
        mood,
        score
    ))

    conn.commit()
    conn.close()


# ---------------- GET LAST LOG ---------------- #

def get_last_log(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT study,
           sleep,
           exercise,
           scroll,
           mood,
           focus_score,
           log_date
    FROM user_logs
    WHERE username=?
    ORDER BY id DESC
    LIMIT 1
    """, (username,))

    data = cursor.fetchone()

    conn.close()

    return data


# ---------------- GET ALL LOGS ---------------- #

def get_all_logs(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        study,
        sleep,
        exercise,
        scroll,
        mood,
        focus_score,
        log_date
    FROM user_logs
    WHERE username=?
    ORDER BY id DESC
    """, (username,))

    rows = cursor.fetchall()

    conn.close()

    return rows


# ---------------- AVERAGE FOCUS ---------------- #

def get_average_focus(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(focus_score)
        FROM user_logs
        WHERE username=?
    """, (username,))

    result = cursor.fetchone()[0]

    conn.close()

    return round(result, 1) if result else 0


# ---------------- TOTAL STUDY ---------------- #

def get_total_study(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(study)
        FROM user_logs
        WHERE username=?
    """, (username,))

    result = cursor.fetchone()[0]

    conn.close()

    return round(result, 1) if result else 0


# ---------------- TOTAL LOGS ---------------- #

def get_total_logs(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM user_logs
        WHERE username=?
    """, (username,))

    result = cursor.fetchone()[0]

    conn.close()

    return result


# ---------------- AVERAGE SLEEP / EXERCISE ---------------- #

def get_average_sleep(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(sleep) FROM user_logs WHERE username=?
    """, (username,))

    result = cursor.fetchone()[0]
    conn.close()

    return round(result, 1) if result else 0


def get_average_exercise(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(exercise) FROM user_logs WHERE username=?
    """, (username,))

    result = cursor.fetchone()[0]
    conn.close()

    return round(result, 1) if result else 0


# ---------------- CURRENT STREAK (consecutive days logged) ---------------- #

def get_current_streak(username):
    """
    Counts how many consecutive days (ending today or yesterday)
    the user has logged data.
    """
    import datetime

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE(log_date) FROM user_logs
        WHERE username=?
        GROUP BY DATE(log_date)
        ORDER BY DATE(log_date) DESC
    """, (username,))

    dates = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not dates:
        return 0

    log_dates = [datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates]

    today = datetime.date.today()
    streak = 0
    expected = today

    for d in log_dates:
        if d == expected:
            streak += 1
            expected = expected - datetime.timedelta(days=1)
        elif d == expected + datetime.timedelta(days=1):
            # still allow if today isn't logged yet, but yesterday is
            continue
        else:
            break

    return streak


# ---------------- SETTINGS ---------------- #

def ensure_settings(username):
    """Create a default settings row for a user if one doesn't exist yet."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO settings(username, dark_mode, notifications)
        VALUES (?, 1, 1)
    """, (username,))

    conn.commit()
    conn.close()


def get_settings(username):

    ensure_settings(username)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dark_mode, notifications FROM settings WHERE username=?
    """, (username,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {"dark_mode": bool(row[0]), "notifications": bool(row[1])}

    return {"dark_mode": True, "notifications": True}


def update_settings(username, dark_mode=None, notifications=None):

    ensure_settings(username)

    current = get_settings(username)

    new_dark_mode = int(dark_mode) if dark_mode is not None else int(current["dark_mode"])
    new_notifications = int(notifications) if notifications is not None else int(current["notifications"])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE settings
        SET dark_mode=?, notifications=?
        WHERE username=?
    """, (new_dark_mode, new_notifications, username))

    conn.commit()
    conn.close()


# ---------------- USER AGE ---------------- #

def get_user_age(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT age FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] is not None:
        return row[0]

    return 18


def set_user_age(username, age):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET age=? WHERE username=?", (age, username))

    conn.commit()
    conn.close()


# ---------------- CHANGE PASSWORD ---------------- #

def change_password(username, new_password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET password=? WHERE username=?
    """, (new_password, username))

    conn.commit()
    conn.close()


# ---------------- ACHIEVEMENTS ---------------- #

def add_achievement(username, badge_name):
    """Insert a badge only if the user doesn't already have it."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM achievements WHERE username=? AND badge_name=?
    """, (username, badge_name))

    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO achievements(username, badge_name)
            VALUES (?, ?)
        """, (username, badge_name))
        conn.commit()

    conn.close()


def get_earned_badges(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT badge_name FROM achievements WHERE username=?
    """, (username,))

    rows = [r[0] for r in cursor.fetchall()]
    conn.close()

    return rows


# ---------------- RESET USER DATA ---------------- #

def reset_user_data(username):
    """Deletes all logs and achievements for a user (keeps the account)."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM user_logs WHERE username=?", (username,))
    cursor.execute("DELETE FROM achievements WHERE username=?", (username,))

    conn.commit()
    conn.close()
