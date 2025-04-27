"""
sender.py
---------
Automates WhatsApp Web interactions using Selenium to send messages.

Key Functions:
  get_driver()      - Launches Chrome with a persistent profile and waits for login.
  pick_message()    - Selects a random template and greeting from the database.
  send_whatsapp()   - Opens a chat by name and types/sends the message via Selenium.
  dispatch()        - Iterates over a list of recipients and sends messages.

Usage:
  dispatch([("Alice", "+1234567890"), ("Bob", "+1987654321")])
"""
import os
import random
import time
import sqlite3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def get_driver():
    """
    Launch Chrome with a persistent user profile so WhatsApp Web stays logged in.
    Waits until the chat list is visible before returning the driver.
    """
    opts = Options()
    # Store login session in local folder
    opts.add_argument(f"--user-data-dir={os.path.abspath('chrome_profile')}")
    # Disable automation banners
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=opts)
    driver.get("https://web.whatsapp.com")

    try:
        # Wait up to 60s for the chat list pane to appear
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chat list']"))
        )
        print("✅ Login successful!")
    except TimeoutException:
        print("❌ Login timed out. Please scan the QR code within 60 seconds.")
        driver.quit()
        raise

    return driver


def pick_message():
    """
    Return a tuple (message_text, is_image_flag).
    Randomly selects 'quote', 'verse', or 'hadith' category from the template table.
    """
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    category = random.choice(['quote', 'verse', 'hadith'])

    c.execute(
        "SELECT content, is_image FROM template WHERE category=? ORDER BY RANDOM() LIMIT 1",
        (category,)
    )
    content, is_image = c.fetchone()
    conn.close()

    # Prepend a suitable greeting based on category
    greetings = {
        'quote': 'Assalamu alaikum! Here’s some motivation:\n\n',
        'verse': 'Salam! A verse for you:\n\n',
        'hadith': 'Peace be upon you. A hadith to reflect on:\n\n'
    }
    return greetings[category] + content, bool(is_image)


def send_whatsapp(driver, contact_name, message, is_image=False):
    """
    Opens a chat with the given contact_name (as shown in WhatsApp UI) and sends the message.
    Supports multi-line messages.
    """
    print(f"🚀 Sending to {contact_name}…")

    try:
        driver.get("https://web.whatsapp.com")
        wait = WebDriverWait(driver, 30)

        # 1) Search for contact by name
        search_xpath = "//div[@role='textbox' and @data-tab='3']"
        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
        # Clear old search text
        search_box.send_keys(Keys.CONTROL + 'a' + Keys.BACKSPACE)
        search_box.send_keys(contact_name)
        time.sleep(1)
        search_box.send_keys(Keys.ENTER)

        # 2) Confirm chat loads by header title
        header_xpath = f"//header//span[@title='{contact_name}']"
        wait.until(EC.presence_of_element_located((By.XPATH, header_xpath)))

        # 3) Locate the message input <p> using full XPath
        p_xpath = ("//*[@id='main']/footer/div[1]/div/span/"
                   "div/div[2]/div[1]/div[2]/div[1]/p")
        input_p = wait.until(EC.element_to_be_clickable((By.XPATH, p_xpath)))

        # 4) Clear the box
        parent_div = input_p.find_element(By.XPATH, './..')
        parent_div.send_keys(Keys.CONTROL + 'a' + Keys.BACKSPACE)

        # 5) Type each line, preserving newlines
        lines = message.split("\n")
        for line in lines[:-1]:
            input_p.send_keys(line + Keys.SHIFT + Keys.ENTER)
        input_p.send_keys(lines[-1] + Keys.ENTER)

        print(f"✅ Message sent to {contact_name}")
        time.sleep(2)

    except TimeoutException as e:
        print(f"⏰ Timeout loading element: {e}")
        raise
    except Exception as e:
        print(f"❌ Error while sending: {e}")
        raise


def dispatch(contacts):
    """
    contacts: list of (contact_name, phone_number) tuples
    Loops through contacts, picks a random message, and sends it.
    """
    driver = get_driver()
    try:
        for name, number in contacts:
            msg, is_img = pick_message()
            send_whatsapp(driver, name, msg, is_img)
    finally:
        driver.quit()
        print("🚩 Closed browser session")
