from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta,date


load_dotenv()

ACCOUNT_EMAIL: str = os.getenv("ACCOUNT_EMAIL") or ""
ACCOUNT_PASSWORD: str = os.getenv("ACCOUNT_PASSWORD") or ""
GYM_URL: str = os.getenv("GYM_URL") or ""



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

        self.finding_all_classes()

    def get_next_weekday(self,target_weekday):
        today = date.today()
        
        days_until_target = (target_weekday - today.weekday()) % 7
        next_target = today + timedelta(days=days_until_target)
        return next_target
            
    def finding_all_classes(self):
        try:
            class_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[id^="class-card-"]')
            next_tuesday_str = self.get_next_weekday(1).strftime("%Y-%m-%d")+'-1800'
            next_day_tuesday = self.get_next_weekday(1).strftime("%a, %b %d ")
            next_thursday_str = self.get_next_weekday(3).strftime("%Y-%m-%d")+'-1800'
            next_day_thursday = self.get_next_weekday(3).strftime("%a, %b %d ")
            booked_classes = 0
            waitlists_joined = 0
            already_booked_waitlisted = 0
            processed_classes = []
            for class_card in class_cards:
                day_label = None  # Reset day_label for the next iteration
                class_id = class_card.get_attribute('id')
                if next_tuesday_str in class_id:
                    day_label = next_day_tuesday
                elif next_thursday_str in class_id:
                    day_label = next_day_thursday
                if day_label:
                    butoon = class_card.find_element(By.TAG_NAME,'button')
                    if butoon.text.lower() == 'book class':
                        butoon.click()
                        booked_classes += 1
                        processed_classes.append(f'[New Booking] {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')
                        print(f'booked class {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')
                    elif butoon.text.lower() == 'booked':
                        already_booked_waitlisted += 1
                        processed_classes.append(f'[Booked]  {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')
                        print(f'Already booked: {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')
                    elif butoon.text.lower() == 'join waitlist':
                        butoon.click()
                        waitlists_joined += 1
                        processed_classes.append(f'[New Waitlist] {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')
                        print(f'Joined waitlist for: {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')
                    elif butoon.text.lower() == 'waitlisted':
                        already_booked_waitlisted += 1
                        processed_classes.append(f'[Waitlisted] {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')
                        print(f'Already on waitlist: {class_card.find_element(By.TAG_NAME,'h3').text} on {day_label}')


            print('--- BOOKING SUMMARY ---')
            print(f"Classes booked: {booked_classes}")
            print(f"Waitlists joined: {waitlists_joined}")
            print(f"Already booked/waitlisted: {already_booked_waitlisted}")
            print(f'Total Tuesday & Thursday 6pm classes: {booked_classes + waitlists_joined + already_booked_waitlisted}')

            print('--- DETAILED CLASS LIST ---')
            for class_ in processed_classes:
                print(f'•{class_}')

        except Exception as e:
            print(f"An error occurred while finding class cards: {e}")
        


if __name__ == "__main__":
    bot = GymBot()
    bot.login()