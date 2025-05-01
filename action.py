# === This code allows you to get a pdf to desktop CPA Questions folder from CPA beckers pratice questions === 

pip install selenium pillow fpdf
pip install Pillow

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import traceback
from selenium.common.exceptions import NoSuchElementException

from PIL import Image

# === CONFIGURATION ===
LOGIN_PAGE_URL = 'https://cpa.becker.com/login'
LOGIN_URL = 'https://cpa.becker.com/module/F-01-01/V1.2/mcqs/session?context=homework&filter=0'
USERNAME = 'effyyu99@gmail.com'
PASSWORD = '!3243546Iloveu'

# Safely joins paths in a way that works on any operating system (Windows, macOS, Linux).
desktop_path = r"C:\Users\eyu\OneDrive - Houlihan Lokey\Desktop\CPA Questions"


# === SETUP CHROME DRIVER ===
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)
driver.execute_script("document.body.style.zoom='200%'")  # Try 150% or 200%
wait = WebDriverWait(driver, 10)

try:
    # === LOGIN ===
    driver.get(LOGIN_PAGE_URL)
    time.sleep(1)

    try:
        cookie_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
        )
        cookie_button.click()
        print("🍪 Accepted cookies.")
    except TimeoutException:
        print("✅ No cookie banner appeared.")

    email_input = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
    password_input = driver.find_element(By.NAME, 'password')

    email_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()

    wait.until(EC.url_changes(LOGIN_PAGE_URL))
    print("✅ Logged in!")


    # === GO TO QUESTION PAGE ===
    driver.get(LOGIN_URL)
    time.sleep(3)

    # === Create an image_list === 
    image_list=[]

    q_counts = 40
    
    for i in range(q_counts): 
        # === FIND TARGET ELEMENT ===
        element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'main[data-qa-label="finalexam-content-box"]'))
            )
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(2)
    
        # === create the name and the path for the image ===
        cropped_path = os.path.join(desktop_path, f"becker_question_{i+1}.png")
        
        # === DIRECTLY CAPTURE ELEMENT ===
        element.screenshot(cropped_path)

        image_list.append(f"becker_question_{i}.png")

        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, NEXT_BUTTON_SELECTOR)))
            next_button.click()
        except TimeoutException:
            print(f"⚠️ Next button not clickable after Question {i+1}")
            break
        time.sleep(2)  # Allow time for the next question to load
        

    print("✅ Cropped screenshot all saved!!! Good Job!!!")

        

except Exception as e:
    print("❌ Error:", str(e))
    traceback.print_exc()


# Replace with your actual list of image paths
image_list = [os.path.join(desktop_path, f"becker_question_{i+1}.png") for i in range(q_counts)]

# Open images
images = [Image.open(img).convert("RGB") for img in image_list]

# Save as a single PDF
pdf_path = os.path.join(desktop_path, "becker_questions.pdf")
if images:
    images[0].save(pdf_path, save_all=True, append_images=images[1:],resolution=300, quality=95)
    print(f"✅ PDF created at: {pdf_path}")
else:
    print("❌ No images found.")

# === Cleanup: 
# 1) === Delete the image files after PDF is saved ===
for img_path in image_list:
    os.remove(img_path)

# List of image file extensions to delete in the folder
image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"]
# Loop through and delete each image file
for filename in os.listdir(desktop_path):
    if any(filename.lower().endswith(ext) for ext in image_extensions):
        file_path = os.path.join(desktop_path, filename)
        os.remove(file_path)
print("✅ All image files deleted.")

# 2) === log out of Becker Account 
driver = webdriver.Chrome()
driver.get("https://www.becker.com/user")
try:
    # Try to find the "Log out" link
    logout_button = driver.find_element(By.LINK_TEXT, "Log out")
    # If found, click it
    logout_button.click()
    print("✅ Logged out.")
except NoSuchElementException:
    print("ℹ️ Log out button not found. Maybe already logged out?")


finally:
    driver.quit()
