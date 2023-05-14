import time
from selenium import webdriver
import instaloader
from instaloader.exceptions import ConnectionException
import telegram
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from dotenv import load_dotenv
import pickle

load_dotenv()


class InstaBot:

    def __init__(self):
        self.ig_url = "https://www.instagram.com/"
        self.insta_username = os.getenv("INSTA_USERNAME")
        self.insta_password = os.getenv("INSTA_PASSWORD")
        self.dm_id = os.getenv("INSTA_DM_ID")
        self.driver = self.initialize_chrome_driver()
        self.chat_id = "@testing_bot_12345"

        # Create an Instaloader instance
        self.L = instaloader.Instaloader(filename_pattern='{profile}_reel')
        self.bot_running = True

        self.message_format = """
        Details for {}
        Reel Owner --> https://www.instagram.com/{}/
        Reel Caption --> {}
        Reel location : {}

        Reel tagged_accounts : {}
        """

        self.failed_message = """
        Failed to get details for {}, {}.
        Please Contant Admin or Try again later.
        """

    @staticmethod
    def initialize_chrome_driver():

        # Create Chrome options instance
        options = Options()

        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)

        # Run in the headless browser
        options.headless = True

        # Setting the driver path and requesting a page
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        # Changing the property of the navigator value for webdriver to undefined
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def stop_bot(self):
        self.bot_running = False

    def login_to_instagram(self):
        """This Function First tries to log into instagram using a cookie session and if it does not find the cookie
        session, it Creates the session using the details provided and then saves the session for subsequest logins
        It also disables the 'enable notification' pop up and the 'save login info' pop up."""

        self.driver.get(self.ig_url)
        print("loaded Instagram site")
        # Check for cookies option
        try:
            time.sleep(5)
            print("searching for cookies page")
            allow_cookie = self.driver.find_element(By.XPATH,
                                               "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]")
        except NoSuchElementException:
            print("Did not find accept cookies element")
            pass

        else:
            allow_cookie.click()

        # Open the instagram url and try to load the cookie session
        try:
            time.sleep(2)
            self.driver.get(self.ig_url)
            cookies = pickle.load(open("ig_cookies.pkl", "rb"))

            for cookie in cookies:
                self.driver.add_cookie(cookie)
                print("Loaded cookies...")

            time.sleep(5)
            self.driver.get(self.ig_url)

        except FileNotFoundError:
            # If it fails to find the cookie session, Login using the regular method
            self.driver.get(self.ig_url)

            # Enter Username and Password and click submit.
            time.sleep(5)
            WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//input[@name="username"]')))
            self.driver.find_element(By.XPATH, '//input[@name="username"]').send_keys(self.insta_username)
            self.driver.find_element(By.XPATH, '//input[@name="password"]').send_keys(self.insta_password)

            time.sleep(1)
            self.driver.find_element(By.XPATH, '//button[@class="_acan _acap _acas _aj1-"]').click()

        # At the popup that asks to save the login info, Click Yes
        try:
            time.sleep(10)
            print("Searching for option to save login info")
            not_now = self.driver.find_element(By.XPATH, '//button[@class="_acan _acap _acas _aj1-"]')
            not_now.click()
            print("Save login button clicked")

            # Save the cookie session id
            print(self.driver.get_cookies())
            pickle.dump(self.driver.get_cookies(), open("ig_cookies.pkl", "wb"))
            print("cookies saved successfully")

        except NoSuchElementException:
            print("Did not find save login button")
            pass

        # Disable option to enable notification
        try:
            print("Checking for Enable Notification button")
            time.sleep(7)
            notif_not_now = self.driver.find_element(By.XPATH, "//button[@class='_a9-- _a9_1']")
            notif_not_now.click()
            print("Clicked Enable Notification button")

        except NoSuchElementException:
            print("Did not find Enable Notification button")

    def send_instagram_reel_to_telegram_group(self, reel_url):
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        bot = telegram.Bot(token=telegram_token)

        # Login to Instagram (only needed for private accounts)
        # L.context.log("Login Required.")
        # L.interactive_login("YOUR_USERNAME")

        # Extract the shortcode from the Instagram reel URL
        shortcode = reel_url.split('instagram.com/reel/')[1].split('/')[0]

        # Get the post from Instagram using the shortcode
        try:
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
        except instaloader.exceptions.ConnectionException:
            print(f"Failed to download media for {reel_url}")
            bot.send_message(chat_id=self.chat_id,
                             text=self.failed_message.format(reel_url, "Connection Error"))
            return False

        # Download the post
        try:
            print("Downloading media. Please wait...")
            self.L.download_post(post, target='#downloads')

        except ConnectionException:
            print("Failed To download IG Reel for {reel_url}. An Error is stopping you from doing so.")
            bot.send_message(chat_id=self.chat_id,
                             text=self.failed_message.format(reel_url, "Connection Error"))

        # Get the downloaded file path
        media_file_path = f"#downloads/{post.owner_username}_reel.mp4"

        # Check if the media file exists
        if not os.path.exists(media_file_path):

            print(f"Failed to download media for {reel_url}")
            bot.send_message(chat_id=self.chat_id,
                             text=self.failed_message.format(reel_url, "Failed to download media" ))
            return False

        # Send the media file to the Telegram group chat
        print("Sending media to Telegram. Please wait...")

        bot.send_video(chat_id=self.chat_id, video=open(media_file_path, 'rb'),
                       caption=self.message_format.format(reel_url,
                                                          post.owner_username,
                                                          post.caption,
                                                          post.location,
                                                          post.tagged_users))

        # Delete the downloaded media file
        dir_path = "#downloads/"

        files = os.listdir(dir_path)

        for file in files:
            if file.startswith(f"{post.owner_username}_reel"):
                os.remove(os.path.join(dir_path, file))

        print(f"Media for {reel_url} sent to Telegram successfully!")

        return True

    def interact_with_instagram(self, current_notif_count=0, dm_id="https://www.instagram.com/direct/t/340282366841710300949128137536014401524"):
        """This Function is called once the bot has logged into the acount and has been able to cancel all popups
        The bot then continually checks to see if the Notification button changes and once it does. The bot immediately
        opens the required DM and then downloads the latest reel sent to  it
        :param int current_notif_count: How many Notifications do you currently have in the ig account
        :param str dm_id: The url of the senders dm when already logged in. To get this login to your ig account using the
        web and open the dm of the account sending the reels and copy the url on the webpage

        """
        # Click on Messaging option

        # Wait till i get a notification
        while self.bot_running:
            try:
                time.sleep(3)
                # Checks if the Notification button has gotten an extra notification

                if current_notif_count == 0:
                    new_notif_xpath = f'//a[@aria-label="Direct messaging - {current_notif_count + 1} new notification link"]'
                else:
                    new_notif_xpath = f'//a[@aria-label="Direct messaging - {current_notif_count + 1} new notifications link"]'

                new_notification = self.driver.find_element(By.XPATH, new_notif_xpath)

                # Once there is a notification, open the DM and get the latest reel.
                self.driver.get(self.dm_id)
                time.sleep(2)

                # Fetch the Reels and get the link for the most recent one.
                print("Fetching Reels...")
                time.sleep(3)
                reels = self.driver.find_elements(By.XPATH, "//div[@class='_acfj']")
                print(reels)

                most_recent_reel = reels[-1]
                # click on the reel
                most_recent_reel.click()
                time.sleep(2)
                # get the current url of the reel
                reel_url = self.driver.current_url
                print(reel_url)

                # Replace the /p/ with /reel/n the url
                mod_reel_url = reel_url.replace('www.instagram.com/p/', 'www.instagram.com/reel/')
                print(mod_reel_url)

                # Send the media to telegram
                self.send_instagram_reel_to_telegram_group(mod_reel_url)
                self.driver.get(self.ig_url)
                time.sleep(2)

            except NoSuchElementException:
                # Wait for 2 seconds before checking again
                time.sleep(2)
                continue
                # Button has changed, break out of the loop

