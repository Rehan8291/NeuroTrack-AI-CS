import sqlite3
from database.db import get_connection, ensure_settings


# ---------------- SIGNUP ---------------- #

def signup(username, password, age=18):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users (username, password, age)
            VALUES (?, ?, ?)
            """,
            (username, password, age)
        )

        conn.commit()

        ensure_settings(username)

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# ---------------- LOGIN ---------------- #

def login(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username
        FROM users
        WHERE username=?
        AND password=?
        """,
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# ---------------- USER EXISTS ---------------- #

def user_exists(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username=?
        """,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user is not None