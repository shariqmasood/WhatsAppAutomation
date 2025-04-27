"""
WhatsApp Automator
------------------
100 Days of Code Assignment: Automate WhatsApp Messaging with Python & Selenium

Overview:
This desktop GUI application lets you schedule and send Islamic motivational quotes,
Quranic verses, and Hadith messages via WhatsApp Web. Features include:
  • Adding friends and groups stored in an SQLite database
  • Choosing between individual or group recipients
  • Scheduling messages for Now, Daily, Weekly, or Monthly dispatch
  • Random selection of message templates for variety

Technologies & Libraries:
  • Python 3.x
  • Tkinter for the GUI
  • APScheduler for job scheduling
  • Selenium WebDriver for WhatsApp Web automation
  • SQLite for persistent storage of contacts and templates

Usage:
 1. Populate `friend`, `grp`, and `template` tables in `db.sqlite` (see models.py).
 2. Run this script (`python app.py`), scan the QR once, then select friends/groups
    and schedule your automated messages.
 3. The app runs in the background, dispatching messages at your chosen intervals.

"""
