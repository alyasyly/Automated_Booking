from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
from dotenv import load_dotenv
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException 

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
        self.wait = WebDriverWait(self.driver, 10)

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

    def finding_all_classes(self):
        try:
            class_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[id^="class-card-"]')

            booked_classes = 0
            waitlists_joined = 0
            already_booked_waitlisted = 0

            for class_card in class_cards:
                class_id = class_card.get_attribute('id') or ""

                match = re.search(r'(\d{4}-\d{2}-\d{2})-(1800)', class_id)
                
                if match:
                    date_str = match.group(1)
                    card_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    

                    if card_date.weekday() in [1, 3]:
                        day_label = card_date.strftime("%a, %b %d")
                        button = class_card.find_element(By.TAG_NAME, 'button')
                        class_name = class_card.find_element(By.TAG_NAME, "h3").text
                        btn_text = button.text.lower()

                        if btn_text == 'book class':
                            button.click()
                            booked_classes += 1
                            print(f'✓ Booked class: {class_name} on {day_label}')

                        elif btn_text == 'booked':
                            already_booked_waitlisted += 1
                            print(f'✓ Already booked: {class_name} on {day_label}')

                        elif btn_text == 'join waitlist':
                            button.click()
                            waitlists_joined += 1
                            print(f'✓ Joined waitlist for: {class_name} on {day_label}')

                        elif btn_text == 'waitlisted':
                            already_booked_waitlisted += 1
                            print(f'✓ Already on waitlist: {class_name} on {day_label}')

            total_expected_classes = booked_classes + waitlists_joined + already_booked_waitlisted
            self.verify_bookings(total_expected_classes)

        except Exception as e:
            print(f"An error occurred while finding class cards: {e}")

    def verify_bookings(self, total):
        print(f"\n--- Total Tuesday/Thursday 6pm classes: {total} ---\n")
        print("--- VERIFYING ON MY BOOKINGS PAGE ---")

        found_count = 0

        try:
            my_bookings_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "My Bookings")))
            my_bookings_link.click()

            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id*='card-']")))

            booked_items = self.driver.find_elements(By.CSS_SELECTOR, 'div[id^="booking-card-"]')
            waitlist_items = self.driver.find_elements(By.CSS_SELECTOR, 'div[id^="waitlist-card"]')

            all_cards = booked_items + waitlist_items

            if not all_cards:
                raise NoSuchElementException

            for card in all_cards:
                try:
                    when_paragraph = card.find_element(By.XPATH, ".//p[strong[text()='When:']]")
                    when_text = when_paragraph.text

                    if ("Tue" in when_text or "Thu" in when_text) and "6:00 PM" in when_text:
                        class_name = card.find_element(By.TAG_NAME, "h3").text
                        card_id = card.get_attribute("id") or ""
                        found_count += 1
                        status = " (Waitlist)" if "waitlist" in card_id else ""
                        print(f"  ✓ Verified: {class_name}{status}")
                except NoSuchElementException:
                    pass

        except NoSuchElementException:
            pass
        except Exception as e:
            print(f"An error occurred during verification: {e}")

        print("\n--- VERIFICATION RESULT ---")
        expected_word = "booking" if total == 1 else "bookings"
        found_word = "booking" if found_count == 1 else "bookings"

        print(f"Expected: {total} {expected_word}")
        print(f"Found: {found_count} {found_word}")

        if total == found_count:
            print("✅ SUCCESS: All bookings verified!")
        else:
            diff = total - found_count
            print(f"❌ MISMATCH: Missing {diff} {expected_word}")


if __name__ == "__main__":
    bot = GymBot()
    bot.login()