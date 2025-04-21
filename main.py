from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# Path to your downloaded ChromeDriver
CHROMEDRIVER_PATH = r"C:\Users\yuvraj\Tools\chromedriver.exe"

# Setup browser options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Start the browser
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Go to register2park
driver.get("https://register2park.com")

# Let it stay open for 10 seconds so we can see it works
time.sleep(10)

# Close the browser
driver.quit()
