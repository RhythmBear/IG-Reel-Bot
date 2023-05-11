import time
from selenium import webdriver
import instaloader
from instaloader.exceptions import ConnectionException
import telegram
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import load_dotenv
import pickle

load_dotenv()


class InstaBot:

    def __init__(self):
        self.ig_url = "https://www.instagram.com/"
        self.insta_username = os.getenv("INSTA_USERNAME")
        self.insta_password = os.getenv("INSTA_PASSWORD")
        self.dm_id = os.getenv("INSTA_DM_ID")
        self.driver = webdriver.Chrome(service=Service("chromedriver.exe"))
        self.chat_id = "@testing_bot_12345"
        # Create an Instaloader instance
        self.L = instaloader.Instaloader(filename_pattern='{profile}_reel')
        self.bot_running = True

        self.message_format = """
        Details for {}
        Reel Owner: {}
        Reel Caption : {}
        Reel location : {}

        Reel tagged_accounts : {}
        """

        self.failed_message = """
        Failed to get details for {}
        Please Contant Admin or Try again later.

        """

    def stop_bot(self):
        self.bot_running = False

    def login_to_instagram(self):
        """This Function First tries to log into instagram using a cookie session and if it does not find the cookie
        session, it Creates the session using the details provided and then saves the session for subsequest logins
        It also disables the 'enable notification' pop up and the 'save login info' pop up."""

        try:
            time.sleep(2)
            self.driver.execute("get", {'url': 'http://www.instagram.com'})
            cookies = pickle.load(open("cookies.pkl", "rb"))

            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.execute("get", {'url': 'http://www.instagram.com'})

        except:
            # If there is an error Login using the regular method

            self.driver = webdriver.Chrome(service=Service("chromedriver.exe"))
            self.driver.get(self.ig_url)

            time.sleep(10)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']"))).send_keys(self.insta_username)
            self.driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(self.insta_password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'] div").click()

            # Save the cookie session id
            pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
            self.driver.quit()

        # Save Login Info
        # DO not save login info
        try:
            time.sleep(5)
            print("Searching for option to save login info")
            not_now = self.driver.find_element(By.XPATH,
                                               "//div[@class='x1i10hfl xjqpnuy xa49m3k xqeqjp1 x2hbi6w xdl72j9 x2lah0s xe8uvvx "
                                               "xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli x1hl2dhg xggy1nq x1ja2u2z x1t137rt "
                                               "x1q0g3np x1lku1pv x1a2a7pz x6s0dn4 xjyslct x1ejq31n xd10rxx x1sy0etr x17r0tee"
                                               " x9f619 x1ypdohk x1i0vuye xwhw2v2 xl56j7k x17ydfre x1f6kntn x2b8uid xlyipyv "
                                               "x87ps6o x14atkfc x1d5wrs8 x972fbf xcfux6l x1qhh985 xm0m39n xm3z3ea "
                                               "x1x8b98j x131883w x16mih1h xt0psk2 xt7dq6l xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 xjbqb8w x1n5bzlp x173jzuc x1yc6y37']")
            not_now.click()
            print("Save login Not now button clicked")

        except NoSuchElementException:
            print("Did not find save login button")
            pass

        # Disbale option to enable notification
        try:
            print("Checking for Enable Notification button")
            time.sleep(5)
            notif_not_now = self.driver.find_element(By.XPATH, "//button[@class='_a9-- _a9_1']")
            notif_not_now.click()

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
            return

        # Download the post
        try:
            print("Downloading media. Please wait...")
            self.L.download_post(post, target='#downloads')

        except ConnectionException:
            print("Failed To download IG Reel for {reel_url}. An Error is stopping you from doing so.")

        # Get the downloaded file path
        media_file_path = f"#downloads/{post.owner_username}_reel.mp4"

        # Check if the media file exists
        if not os.path.exists(media_file_path):
            print(f"Failed to download media for {reel_url}")
            return

        # Send the media file to the Telegram group chat
        print("Sending media to Telegram. Please wait...")
        bot = telegram.Bot(token=telegram_token)
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

    def interact_with_instagram(self):
        """This Function is called once the bot has logged into the acount and has been able to cancel all popups
        The bot then continually checks to see if the Notification button changes and once it does. The bot immediately
        opens the required DM and then downloads the latest reel sent to  it """
        # Click on Messaging option

        # Wait till i get a notification
        while True:
            try:
                time.sleep(3)
                # Checks if the Notification button has gotten an extra notification
                new_notification = self.driver.find_element(By.XPATH,
                                                            '//a[@aria-label="Direct messaging - 4 new notifications link"]')

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

