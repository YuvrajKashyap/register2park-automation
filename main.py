from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# this works for me bc i have my own config file, but it'll go to the template if you don't have one

try:
    from config import APARTMENT, MAKE, MODEL, PLATE
except ImportError:
    from config_template import APARTMENT, MAKE, MODEL, PLATE



# path to your downloaded ChromeDriver
CHROMEDRIVER_PATH = r"C:\Users\yuvraj\Tools\chromedriver.exe"

# setup browser options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# start the browser
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# go to register2park
driver.get("https://register2park.com")


# had to use WebDriverWait because web takes a while to load

try:
    # wait up to 10 seconds for the "Register Vehicle" button to show up
    register_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-lg.btn-info"))
    )


    # click the red register vehicle button
    register_button.click()
    print("Clicked 'Register Vehicle'")



    # types Camelot in the search bar
    search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "propertyName"))
    )
    
    search_input.clear()
    search_input.send_keys("Camelot")
    print("Entered 'Camelot' into property search")
    
    # clicks the Next button
    next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "confirmProperty"))
    )
    next_button.click()
    print("Clicked 'Next'... going to next page")
    
    #clicks the select button for camelot
    select_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.select-property"))
    )
    select_button.click()
    print("Clicked 'Select' for Camelot - Richardson")
    
    
    #click on visitor parking button
    visitor_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "registrationTypeVisitor"))
    )
    visitor_button.click()
    print("Clicked 'Visitor Parking' to enter car info form")
    
    
    
    #wait till everything loads in

    apt_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "vehicleApt"))
    )
    
    make_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "vehicleMake"))
    )
    model_input = driver.find_element(By.ID, "vehicleModel")
    plate_input = driver.find_element(By.ID, "vehicleLicensePlate")
    confirm_plate_input = driver.find_element(By.ID, "vehicleLicensePlateConfirm")
    
    
    #fill in the apartment number
    apt_input.clear()
    apt_input.send_keys(APARTMENT)  # <-- apartment number
    print("Entered apartment number + filling in car info")
    
    
    #fill in make of car
    make_input.clear()
    make_input.send_keys(MAKE) # <-- make of car
    
    # fill in model of car
    model_input.clear()
    model_input.send_keys(MODEL) # <-- model of car
    
    # fill in license plate
    plate_input.clear()
    plate_input.send_keys(PLATE)
    
    # confirm license plate
    confirm_plate_input.clear()
    confirm_plate_input.send_keys(PLATE)
    
    #click next button
    
    next_submit = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "vehicleInformation"))
    )
    next_submit.click()
    
    print("Submitted the parking registration form!")
   
    
except Exception as e:
    
    print("Error: Could not find the 'Register Vehicle' button.")
    print(str(e))
    
    
    





# let it stay open for 10 seconds so we can see it works
time.sleep(10)

# close the browser
driver.quit()



