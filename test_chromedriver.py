# test_chromedriver.py
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

try:
    # This single call will trigger Selenium Manager to fetch the 135.x driver
    driver = webdriver.Chrome()
    print("✅ ChromeDriver OK — browser version:",
          driver.capabilities.get("browserVersion"))
    driver.quit()
except WebDriverException as e:
    print("❌ Error starting ChromeDriver:", e)
