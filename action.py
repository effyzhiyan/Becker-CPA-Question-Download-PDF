# === imports === 
# loads the Streamlit Module to create a web UI 
import streamlit as st 

# credential file (Allows remember me function)
import json

# os: Handles file paths and directory checks
# time: Use for delays (sleep) 
# tempfile: creates a temporary directoory to store screenshots 
import os 
import time
import tempfile

# PIL (Pillow): process and merge images into PDF
from PIL import Image

# Selenium: automates browser interaction
# by: helps locate elements by attributes (e.g. name, CSS selector)
# options: customize browser behavior ( like headless mode) 
# webdriverwait + EC: adds wait to make sure elements load before interacting
# Exceptions: catches issues like elements not loading or not found 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException








# === Streamlit UI setup ===
# This is the main title: Becker CPA Question Downloader 
st.title("📘 Becker CPA Question Downloader")

# Remember me credential file storage setup 
CRED_FILE = "credentials.json"

# define the credientials functions
def load_credentials():
    if os.path.exists(CRED_FILE):
        with open(CRED_FILE, "r") as f:
            return json.load(f)
    return {"username": "", "password": ""}
def save_credentials(username, password):
    with open(CRED_FILE, "w") as f:
        json.dump({"username": username, "password": password}, f)
        
# 1) Load any saved creds
creds = load_credentials()


# These are the main inputs fields:  
# st.text_input(label, value="", max_chars= , type=""...) 
login_url = st.text_input("🔗 Becker MCQ URL", value="")
username = st.text_input("📧 Becker Username (Email)", type="default",  value=creds["username"])
password = st.text_input("🔒 Becker Password", type="password", value=creds["password"])
# output_folder = st.text_input("📂 Output Folder (e.g., C:/Users/YourName/Desktop)", value=r"")
# 2) Show form with a Remember-me checkbox
remember = st.checkbox("Remember me", value=bool(creds["username"]))






start_button = st.button("Get my screenshots!")

if start_button:
    # check if the path does exist 
    # clean up the path of the folder file first 
    # cleaned_path = os.path.normpath(output_folder.strip().strip('"'))
    if not all([login_url.strip(), username.strip(), password.strip()]):
        st.error("❌ All fields must be filled in.")
    else:
        
 #      st.success(f"✅ Folder exists: {cleaned_path}")
        # spinner to show something is happening; try-except ensures graceful failure
        with st.success("✅ All inputs are valid! Starting the process..."), st.spinner("Running ... please be patient, it might take 60 seconds..."):
            try:
                # Setup headless browser
                chrome_options = Options() # customize the behavior of Chrome browser (e.g. run headlessly, set window sizes)
                chrome_options.add_argument("--headless=new") # run headless mode
                chrome_options.add_argument("--window-size=1920,1080")
                driver = webdriver.Chrome(options=chrome_options)
                wait = WebDriverWait(driver, 2)

                # Login
                driver.get("https://cpa.becker.com/login")
                # tries to accept cookies
                try:
                    cookie_button = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
                    )
                    cookie_button.click()
#                    st.success("🍪 Accepted cookies.")
                except TimeoutException:
                    pass

                # Fills in login credentials and clicks submit 
                email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                password_input = driver.find_element(By.NAME, "password")
                email_input.send_keys(username)
                password_input.send_keys(password)
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                wait.until(EC.url_changes("https://cpa.becker.com/login"))
#                st.success("✅ Logged in!")



                # 3. Save or clear credentials based on checkbox
                if remember:
                    save_credentials(username, password)
                else:
                    if os.path.exists(CRED_FILE):
                        os.remove(CRED_FILE)




                # Navigate to question page
                driver.get(login_url)
                time.sleep(3)

                # created a temporary directory for image storage
                tmp_dir = tempfile.mkdtemp()
                image_list = []
                NEXT_BUTTON_SELECTOR = 'button[data-qa-label="navigation-next-button"]'
                
                # Find the largested number question count 
                # Give page some time to load
                driver.implicitly_wait(5)

                # Extract all Question buttons with the matching class
                q_buttons = driver.find_elements(By.CSS_SELECTOR, "button.finalexam-navigation-top__item")

                # Extract numbers from button text
                question_count = []
                for btn in q_buttons:
                    text = btn.text.strip()
                    if text.isdigit():
                        question_count.append(int(text))
                question_count= max(question_count)

                # Loop through questions
                # get the screenshot 
                for i in range(question_count):
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'main[data-qa-label="finalexam-content-box"]'))
                    )
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    time.sleep(2)
                    
                    # saves each question screenshot to my temporary directory
                    image_path = os.path.join(tmp_dir, f"question_{i+1}.png")
                    element.screenshot(image_path)
                    image_list.append(image_path)
                
                # click next bottom
                    try:
                        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, NEXT_BUTTON_SELECTOR)))
                        next_button.click()
                        time.sleep(2)
                    except TimeoutException:
                        break

                # Create PDF
                images = [Image.open(img).convert("RGB") for img in image_list]
                pdf_path = os.path.join(tmp_dir, "becker_questions.pdf")
                if images:
                    images[0].save(pdf_path, save_all=True, append_images=images[1:], resolution=300, quality=95)
                    with open(pdf_path, "rb") as f:
    #                   st.success(f"✅ PDF created at: {pdf_path}")
                        st.download_button("📥 Download PDF", f, file_name="becker_questions.pdf", mime="application/pdf")


                      
                else:
                    st.error("No screenshots were taken.")

                # Log out (optional)
                driver.get("https://www.becker.com/user")
                try:
                    logout_button = driver.find_element(By.LINK_TEXT, "Log out")
                    logout_button.click()
                except NoSuchElementException:
                    pass

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                # shut down chrome
                driver.quit()
                # delete the temp files and directory
                import shutil
                shutil.rmtree(tmp_dir)
