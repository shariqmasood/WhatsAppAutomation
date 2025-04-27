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
import sqlite3
import os
from tkinter import *
from tkinter import ttk, messagebox
from apscheduler.schedulers.background import BackgroundScheduler
from sender import dispatch

# ----- Database Access Functions -----

def get_friends():
    """
    Fetch all friends from the database.
    Returns a list of (id, name, number).
    """
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("SELECT id, name, number FROM friend")
    rows = c.fetchall()
    conn.close()
    return rows


def get_groups():
    """
    Fetch all groups and their member phone numbers.
    Returns:
      - groups: dict of {group_id: group_name}
      - members: dict of {group_id: [phone_numbers]}
    """
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("SELECT id, name FROM grp")
    group_rows = c.fetchall()

    members = {}
    for gid, _ in group_rows:
        c.execute(
            "SELECT number FROM friend f JOIN group_member gm ON f.id=gm.friend_id WHERE gm.group_id=?",
            (gid,)
        )
        members[gid] = [r[0] for r in c.fetchall()]
    conn.close()

    groups = {gid: name for gid, name in group_rows}
    return groups, members


# ----- Scheduler Initialization -----
sched = BackgroundScheduler()
sched.start()


def schedule_job(is_group, target_id, interval_type):
    """
    Schedule or run the WhatsApp dispatch job immediately or at intervals.
    """
    job_id = 'whatsapp_job'
    # Remove existing job if present
    if sched.get_job(job_id):
        sched.remove_job(job_id)

    def job_func():
        """
        Build contact list and dispatch messages via sender.dispatch().
        """
        contacts = []  # list of (name, number) tuples
        if is_group:
            # Map group members' numbers back to their names
            friend_map = {num: name for (_id, name, num) in friends}
            for num in groups_members[target_id]:
                if num in friend_map:
                    contacts.append((friend_map[num], num))
        else:
            # Single friend selection
            fid, name, num = next(f for f in friends if f[0] == target_id)
            contacts.append((name, num))

        if not contacts:
            print("⚠️ No valid contacts found to send.")
            return

        # Dispatch messages
        dispatch(contacts)

    # If "Now", run once; otherwise schedule recurring
    if interval_type == 'Now':
        job_func()
    else:
        cron_args = {}
        if interval_type == 'Daily':
            cron_args = {'trigger': 'interval', 'days': 1}
        elif interval_type == 'Weekly':
            cron_args = {'trigger': 'interval', 'weeks': 1}
        elif interval_type == 'Monthly':
            cron_args = {'trigger': 'cron', 'day': 1}

        sched.add_job(job_func, id=job_id, **cron_args)


# ----- Tkinter GUI Construction -----
root = Tk()
root.title("WhatsApp Automator")
root.geometry('400x240')  # Slightly larger for readability
root.resizable(False, False)

# Load data
friends = get_friends()
groups, groups_members = get_groups()

# Ensure contacts exist
if not friends and not groups:
    messagebox.showerror(
        "No Contacts/Groups",
        "Add at least one friend or group in the database before scheduling."
    )
    root.destroy()
    exit()

# Row 0: Recipient Type
Label(root, text="Send To:").grid(row=0, column=0, padx=10, pady=10, sticky=W)
send_var = StringVar(value='Friend')
Radiobutton(root, text='Friend', variable=send_var, value='Friend').grid(row=0, column=1, sticky=W)
Radiobutton(root, text='Group',  variable=send_var, value='Group').grid(row=0, column=2, sticky=W)

# Row 1: Friend Selection
Label(root, text="Friend:").grid(row=1, column=0, padx=10, sticky=E)
friend_names = [f[1] for f in friends]
friend_var = StringVar(value=friend_names[0])
friend_cb = ttk.Combobox(root, textvariable=friend_var, values=friend_names, state='readonly')
friend_cb.grid(row=1, column=1, columnspan=2, sticky=W+E, padx=10)

# Row 2: Group Selection
Label(root, text="Group:").grid(row=2, column=0, padx=10, sticky=E)
group_names = list(groups.values())
group_var = StringVar(value=group_names[0] if group_names else '')
group_cb = ttk.Combobox(root, textvariable=group_var, values=group_names, state='readonly')
group_cb.grid(row=2, column=1, columnspan=2, sticky=W+E, padx=10)

# Row 3: Interval
Label(root, text="Interval:").grid(row=3, column=0, padx=10, sticky=E)
interval_var = StringVar(value='Now')
interval_cb = ttk.Combobox(
    root, textvariable=interval_var,
    values=['Now', 'Daily', 'Weekly', 'Monthly'], state='readonly'
)
interval_cb.grid(row=3, column=1, columnspan=2, sticky=W+E, padx=10)

# Row 4: Start Button
start_btn = ttk.Button(root, text="Start", width=20, command=lambda: on_start())
start_btn.grid(row=4, column=1, pady=20)

# Row 5: Feedback Label
task_lbl = Label(root, text="Ready to schedule messages.")
task_lbl.grid(row=5, column=0, columnspan=3)

# ----- Callback Function -----

def on_start():
    """
    Triggered when Start is clicked. Resolves recipient and schedules the job.
    """
    recipient_type = send_var.get()
    interval = interval_var.get()

    if recipient_type == 'Friend':
        idx = friend_names.index(friend_var.get())
        target_id = friends[idx][0]
        is_group = False
    else:
        idx = group_names.index(group_var.get())
        target_id = list(groups.keys())[idx]
        is_group = True

    schedule_job(is_group, target_id, interval)
    task_lbl.config(
        text=f"Scheduled {recipient_type} '{friend_var.get() if not is_group else group_var.get()}' → {interval}"
    )

# ----- Start the GUI event loop -----
root.mainloop()
