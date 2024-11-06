from datetime import datetime

import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="myuser",
        password="mypassword",
        host="localhost",
        port="5432"
    )

# Add meeting
def add_meeting(unixDate, aliases, details, url, creator_id) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    url=url[8:]
    try:
        cursor.execute(
            "INSERT INTO meetings (creator_id, aliases, time, description, link_to_meeting) VALUES (%s, %s, %s, %s, %s)",
            (creator_id, aliases, unixDate, details, url) # TODO: add aliases column
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding meeting: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Get user's meetings
def get_users_meetings(creator_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    meetings = []
    try:
        cursor.execute("SELECT time FROM meetings WHERE creator_id = %s", (creator_id,))
        rows = cursor.fetchall()
        meetings = [row[0] for row in rows]
        return meetings
    except Exception as e:
        print(f"Error fetching meetings: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Delete user
def delete_user(id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s", (id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Add user
def add_user(id: int, alias: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    alias="@"+alias
    try:
        cursor.execute(
            "INSERT INTO users (user_id, alias, date_registered) VALUES (%s, %s, %s)",
            (id, alias, datetime.now().timestamp())  # Assuming 0 for date_registered for now
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Check if meeting URL exists
def meeting_url_exists(url: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM meetings WHERE link_to_meeting = %s", (url,))
        meeting = cursor.fetchone()
        return meeting is not None
    except Exception as e:
        print(f"Error checking meeting URL: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Check if user exists
def user_exists(alias: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE alias = %s", (alias,))
        user = cursor.fetchone()
        return user is not None
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Delete meeting by URL
def delete_meeting_by_url(url: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM meetings WHERE link_to_meeting = %s", (url,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting meeting by URL: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Get meeting creator ID
def get_meeting_creator_id(meeting_url: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM meetings LIMIT 1")
        result = cursor.fetchone()
        return result[1] if result else 0
    except Exception as e:
        print(f"Error getting meeting creator ID: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()


def get_id_by_alias(alias: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT user_id FROM users WHERE alias = %s", (alias,))
        row = cursor.fetchone()

        if row is not None:
            return row[0]
        else:
            return 0
    except Exception as e:
        print(f"Error fetching user ID by alias: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()


def get_alias_by_id(user_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT alias FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()

        if row is not None:
            return row[0]
        else:
            return ""
    except Exception as e:
        print(f"Error fetching alias by user_id: {e}")
        return ""
    finally:
        cursor.close()
        conn.close()

def get_all_meetings() -> list:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM meetings")
        meetings = cursor.fetchall()
        meetings_list = []

        for meeting in meetings:
            meeting_dict = {
                "meeting_id": meeting[0],
                "creator_id": meeting[1],
                "aliases": meeting[2],
                "time": meeting[3],
                "description": meeting[4],
                "link_to_meeting": meeting[5]
            }
            meetings_list.append(meeting_dict)

        return meetings_list

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        cursor.close()
        conn.close()
