from selenium.webdriver.common import keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time, os
import logging
import pandas
import pyperclip
import platform
from constants import *
import functools
import time
from utils import copy_image_to_clipboard



def retry(max_attempts=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    logging.warning(
                        f"Retry {attempt}/{max_attempts} failed: {e}"
                    )
                    time.sleep(delay)
        return wrapper
    return decorator


#how to use this 
# @retry(max_attempts=3, delay=3)
# def send_message(self, phone_no, message):
#     ...



def get_ctrl_key():
    if platform.system() == "Darwin":
        return Keys.COMMAND
    return Keys.CONTROL

logginglevel = logging.INFO



logger = logging.getLogger(__name__)
hdlr = logging.StreamHandler()
logger.setLevel(level=logginglevel)
logger.addHandler(hdlr=hdlr)


class Whatsapp:
    def __init__(self):
        logging.info("Logging Into Whatsapp")
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-infobars")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")

        #IF YOU WANT TO USE A SPECIFIC CHROME PROFILE
        # options.add_argument(r"--user-data-dir=C:\Users\thaku\AppData\Local\Google\Chrome\User Data")
        # options.add_argument("--profile-directory=Profile 1")
        # options. .set_preference("media.navigator.permission.disabled", True)


        logger.debug("\tLaunching browser Instance.")

        driver = webdriver.Chrome(options=options)  # , use_subprocess=True)
        wait_60 = WebDriverWait(driver, 60)
        driver.get("https://web.whatsapp.com/")
        self.CTRL_KEY = get_ctrl_key()

        try:
            # verifying login
            logger.debug("\tWaiting for login.")
            wait_60.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,HEADER,  # heading Whatsapp written on TOP.
                    )
                )
            ).text
            time.sleep(5)
            logger.info("Login sucessfull.")
            self.driver = driver
            self.wait_10 = WebDriverWait(self.driver, 60)
        except:
            driver.close()
            driver.quit()
            raise Exception("--Whatsapp Login Failed")

    @retry(max_attempts=3, delay=3)
    def send_message(self, phone_no, message):
        pyperclip.copy(message)
        try:
            logger.info(f"Sending message to {phone_no}:")

            logger.debug("\tOpening the chat.")
            # open a chat
            self.wait_10.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,SEARCHBAR,  # clicking the textbox input
                    )
                )
            )

            inputbar = self.driver.find_element(
                By.XPATH,SEARCHBAR,  # name/phone text box input
            )

            logger.debug("\tInput bar input.")

            ActionChains(self.driver).move_to_element(inputbar).click().send_keys(
                phone_no
            ).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
            time.sleep(1)

            messageinputbar = self.driver.find_element(
                By.XPATH, MESSAGE_INPUT_BAR,
            )

            logger.debug("\tmessage bar input and sending.")

            ActionChains(self.driver).move_to_element(
                messageinputbar
            ).click().key_down(self.CTRL_KEY).send_keys("v").key_up(self.CTRL_KEY).send_keys(Keys.ENTER).perform()
            time.sleep(1)

            logger.debug("\tmessage sent.")
        except Exception as e:
            logger.error(f"--Error occurred while sending the message: {e}")


    @retry(max_attempts=3, delay=3)
    def send_photo_video_with_message(self, phone_no, path, message=""):
        logger.info(f"Sending photo/video to {phone_no}: {path}")

        if not os.path.isfile(path):
            logger.error(f"--FileNotFoundException: Invalid File Path : {path}")
            return

        try:
            self.wait_10.until(EC.presence_of_element_located((By.XPATH, SEARCHBAR)))
            inputbar = self.driver.find_element(By.XPATH, SEARCHBAR)

            ActionChains(self.driver)\
                .move_to_element(inputbar)\
                .click()\
                .key_down(self.CTRL_KEY)\
                .send_keys("a")\
                .key_up(self.CTRL_KEY)\
                .send_keys(phone_no)\
                .send_keys(Keys.ENTER)\
                .perform()

            time.sleep(1)

            copy_image_to_clipboard(path)

            message_box = self.driver.find_element(By.XPATH, MESSAGE_INPUT_BAR)

            ActionChains(self.driver)\
                .move_to_element(message_box)\
                .click()\
                .key_down(self.CTRL_KEY)\
                .send_keys("v")\
                .key_up(self.CTRL_KEY)\
                .perform()

            time.sleep(4)

            if message:
                pyperclip.copy(message)
                caption_box = self.wait_10.until(
                    EC.presence_of_element_located((By.XPATH, MESSAGE_BOX_AFTER_SELECTING_PHOTO))
                )

                ActionChains(self.driver)\
                    .move_to_element(caption_box)\
                    .click()\
                    .key_down(self.CTRL_KEY)\
                    .send_keys("v")\
                    .key_up(self.CTRL_KEY)\
                    .perform()

            time.sleep(1)

            sendbutton = self.wait_10.until(
                EC.element_to_be_clickable((By.XPATH, SEND_BUTTON))
            )
            sendbutton.click()

            logger.info("Photo/video sent successfully.")
            time.sleep(2)

        except Exception as e:
            logger.error(f"--Error occurred while sending the photo/video: {e}")

    def close(self):
        logger.info("Closing the session.")
        self.driver.close()
        self.driver.quit()
        logger.debug("\tBrowser closed.")


#reading CSV
contacts = pandas.read_csv("contacts.csv")
print(contacts.columns.tolist())
wh = Whatsapp()


message = """
 hey, how are you?
"""

#execution
image_path = "C:/Users/thaku/OneDrive/Desktop/Miscellaneous/Predator_Wallpaper_01_3840x2400.jpg"
for number in contacts["Phone - Value"]:  # contacts["First Name"]:
    print(number)
    wh.send_photo_video_with_message(
        str(number), 
        image_path,
        message
    )
