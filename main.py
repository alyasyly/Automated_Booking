from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv


load_dotenv()

ACCOUNT_EMAIL = os.getenv("ACCOUNT_EMAIL")
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")
GYM_URL = os.getenv("GYM_URL")



class GymBot:
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("detach", True)
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        self.chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(GYM_URL)

        self.wait = WebDriverWait(self.driver,10)


    def login(self):
        try:
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'login-button')))
            login_button.click()

            email_input = self.wait.until(EC.presence_of_element_located((By.ID, 'email-input')))
            email_input.clear()
            email_input.send_keys(ACCOUNT_EMAIL)

            password_input = self.driver.find_element(By.ID, 'password-input')
            password_input.clear()
            password_input.send_keys(ACCOUNT_PASSWORD)

            submit_button = self.driver.find_element(By.ID, 'submit-button')
            submit_button.click()


            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Schedule_scheduleTitle__zfZxg')))
            print("Login successful!")
        except Exception as e:
            print(f"An error occurred during login: {e}")


        


if __name__ == "__main__":
    bot = GymBot()
    bot.login()