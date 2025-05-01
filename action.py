# === imports === 
# loads the Streamlit Module to create a web UI 
import streamlit as st 

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

# These are the main inputs fields:  
# st.text_input(label, value="", max_chars= , type=""...) 
login_url = st.text_input("🔗 Becker MCQ URL", value="")
username = st.text_input("📧 Becker Username (Email)", value="", type="default")
password = st.text_input("🔒 Becker Password", value="", type="password")
question_count = st.number_input("🔢 Number of Questions", min_value=1, max_value=100, value=10)
output_folder = st.text_input("📂 Output Folder (e.g., C:/Users/YourName/Desktop)", value=r"")

start_button = st.button("Start Download")

if start_button:
    if not os.path.exists(output_folder):
        st.error("❌ The specified output folder does not exist.")
    else:
        with st.spinner("Running automation..."):
            try:
                # Setup headless browser
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--window-size=1920,1080")
                driver = webdriver.Chrome(options=chrome_options)
                wait = WebDriverWait(driver, 10)

                # Login
                driver.get("https://cpa.becker.com/login")
                try:
                    cookie_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
                    )
                    cookie_button.click()
                except TimeoutException:
                    pass

                email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                password_input = driver.find_element(By.NAME, "password")
                email_input.send_keys(username)
                password_input.send_keys(password)
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                wait.until(EC.url_changes("https://cpa.becker.com/login"))

                # Navigate to question page
                driver.get(login_url)
                time.sleep(3)

                tmp_dir = tempfile.mkdtemp()
                image_list = []
                NEXT_BUTTON_SELECTOR = 'div.q-navigation-arrow-right'

                for i in range(question_count):
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'main[data-qa-label="finalexam-content-box"]'))
                    )
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    time.sleep(2)

                    image_path = os.path.join(tmp_dir, f"question_{i+1}.png")
                    element.screenshot(image_path)
                    image_list.append(image_path)

                    try:
                        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, NEXT_BUTTON_SELECTOR)))
                        next_button.click()
                        time.sleep(2)
                    except TimeoutException:
                        break

                # Create PDF
                images = [Image.open(img).convert("RGB") for img in image_list]
                pdf_path = os.path.join(output_folder, "becker_questions.pdf")
                if images:
                    images[0].save(pdf_path, save_all=True, append_images=images[1:], resolution=300, quality=95)
                    with open(pdf_path, "rb") as f:
                        st.success(f"✅ PDF created at: {pdf_path}")
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
                driver.quit()
