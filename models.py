"""
models.py
---------
Defines and initializes the SQLite database schema for the WhatsApp Automator project.

Tables:
  friend        - Stores individual contacts (id, name, number).
  grp           - Stores group names (id, name).
  group_member  - Links friends to groups (group_id, friend_id).
  template      - Holds message templates by category (quote, verse, hadith) and an image flag.

Usage:
  Call init_db() once at application start to ensure all tables exist.
"""
import sqlite3


def init_db():
    """
    Create the required tables if they do not already exist.
    """
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()

    # Table for individual friends
    c.execute('''
        CREATE TABLE IF NOT EXISTS friend (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            number TEXT UNIQUE NOT NULL  -- E.164 formatted phone number
        )
    ''')

    # Table for group definitions
    c.execute('''
        CREATE TABLE IF NOT EXISTS grp (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL    -- Unique group name
        )
    ''')

    # Association table linking friends to groups
    c.execute('''
        CREATE TABLE IF NOT EXISTS group_member (
            group_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES grp(id),
            FOREIGN KEY(friend_id) REFERENCES friend(id)
        )
    ''')

    # Table for message templates (quotes, verses, hadiths)
    c.execute('''
        CREATE TABLE IF NOT EXISTS template (
            id INTEGER PRIMARY KEY,
            category TEXT               -- must be one of ('quote','verse','hadith')
                CHECK(category IN ('quote','verse','hadith')),
            content TEXT NOT NULL,     -- message text or image URL
            is_image INTEGER DEFAULT 0  -- flag: 1 if content is image
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()
