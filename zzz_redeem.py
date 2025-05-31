from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

import os
import time

# --- Configuration ---
# URL of the rewards page
REWARDS_URL = "https://act.hoyolab.com/bbs/event/signin/zzz/e202406031448091.html?act_id=e202406031448091"

DRIVER_PATH = None # Set this if chromedriver is not in your PATH       

# --- NEW: HoYoLAB Login Credentials ---
# IMPORTANT: Replace with your actual HoYoLAB username and password
load_dotenv()

HOYOLAB_USERNAME = os.getenv("HOYOLAB_USERNAME")
HOYOLAB_PASSWORD = os.getenv("HOYOLAB_PASSWORD")

def attempt_login(driver):
    """
    Attempts to log into HoYoLAB.
    You WILL likely need to adjust the selectors (By.ID, By.NAME, By.XPATH) for the
    username field, password field, and login button based on the actual HoYoLAB login page structure.
    """
    print("Attempting to log in...")

    # --- Common selectors for login elements (THESE ARE GUESSES AND LIKELY NEED ADJUSTMENT) ---
    # Option 1: Login might be on a separate page or a prominent modal.
    # These selectors are very generic.
    username_field_selectors = [
        (By.NAME, "account"),
        (By.NAME, "username"),
        (By.ID, "username"),
        (By.XPATH, "//input[@placeholder='Email/Username']"), # Common placeholder
        (By.XPATH, "//input[contains(@class, 'login-account-input')]"), # Common class pattern
        (By.XPATH, "//input[@type='text' and contains(@class, 'account')]"),
    ]
    password_field_selectors = [
        (By.NAME, "password"),
        (By.ID, "password"),
        (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//input[contains(@class, 'login-password-input')]"), # Common class pattern
    ]
    login_button_selectors = [
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]"),
        (By.XPATH, "//button[contains(@class, 'login-btn')]"),
        (By.XPATH, "//div[contains(@class, 'login-btn')]"), # Sometimes login buttons are divs
    ]
    # --- End of common selectors ---

    try:
        # Check if a login button/link is present on the event page to trigger the login modal/page
        # This is a common pattern for event pages that require login.
        # You might need to click a "Log In" button first to reveal the username/password fields.
        # Example:
        # login_prompt_button_xpath = "//div[contains(@class, 'login-button') or contains(text(), 'Log In')]"
        # try:
        #     login_prompt_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, login_prompt_button_xpath))
        #     )
        #     print("Found a login prompt button, clicking it...")
        #     login_prompt_button.click()
        #     time.sleep(2) # Wait for modal/page to load
        # except TimeoutException:
        #     print("No separate login prompt button found, assuming login fields are directly available or login already occurred.")


        # Find and fill username field
        username_field = None
        for by, value in username_field_selectors:
            try:
                username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((by, value)))
                print(f"Found username field with: {by}='{value}'")
                break
            except TimeoutException:
                continue
        if not username_field:
            print("ERROR: Could not find the username field with tried selectors.")
            print("Please inspect the login form and update 'username_field_selectors'.")
            return False
        username_field.send_keys(HOYOLAB_USERNAME)
        time.sleep(0.5) # Small delay

        # Find and fill password field
        password_field = None
        for by, value in password_field_selectors:
            try:
                password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((by, value)))
                print(f"Found password field with: {by}='{value}'")
                break
            except TimeoutException:
                continue
        if not password_field:
            print("ERROR: Could not find the password field with tried selectors.")
            print("Please inspect the login form and update 'password_field_selectors'.")
            return False
        password_field.send_keys(HOYOLAB_PASSWORD)
        time.sleep(0.5) # Small delay

        # Find and click login button
        login_button = None
        for by, value in login_button_selectors:
            try:
                login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
                print(f"Found login button with: {by}='{value}'")
                break
            except TimeoutException:
                continue
        if not login_button:
            print("ERROR: Could not find the login button with tried selectors.")
            print("Please inspect the login form and update 'login_button_selectors'.")
            return False

        login_button.click()
        print("Login button clicked.")

        # Wait for login to complete (e.g., by checking if URL changes or a specific element appears/disappears)
        # This is a simple check; a more robust one would be better.
        # For example, wait for the username field to disappear or for a known element on the logged-in page.
        time.sleep(5) # Wait for page to reload or login to process

        # Check if login was successful (very basic check: are we still on a page with "login" in URL?)
        # A better check would be to look for a user profile element or if the login form is gone.
        if "login" in driver.current_url.lower() or "signin" in driver.current_url.lower(): # HoYo might use "signin" for login pages
            # Try to find an error message
            error_message_selectors = [
                (By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'form-error')]"), # General error class
                (By.XPATH, "//div[contains(text(), 'Incorrect') or contains(text(), 'Invalid')]") # Common error text
            ]
            error_found = False
            for by, value in error_message_selectors:
                try:
                    error_element = driver.find_element(by, value)
                    if error_element.is_displayed():
                        print(f"Login possibly failed. Error message found: {error_element.text}")
                        error_found = True
                        break
                except NoSuchElementException:
                    continue
            if not error_found:
                 print("Login might have failed (still on a login-like URL, but no specific error message found).")
            return False

        print("Login presumed successful.")
        return True

    except TimeoutException:
        print("ERROR: Timed out waiting for a login element. The login page structure might be different.")
        print("Please inspect the login form and update the selectors in 'attempt_login' function.")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during login: {e}")
        return False

def main():
    """
    Main function to navigate to the HoYoLAB event page, log in, and attempt to claim rewards.
    """
    if HOYOLAB_USERNAME == "YOUR_USERNAME" or HOYOLAB_PASSWORD == "YOUR_PASSWORD":
        print("-" * 70)
        print("!!! IMPORTANT ACTION REQUIRED !!!")
        print("Please update HOYOLAB_USERNAME and HOYOLAB_PASSWORD in the script with your credentials.")
        print("-" * 70)
        return

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument('--headless') # Uncomment for headless mode

    if DRIVER_PATH:
        driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    try:
        print(f"Navigating to: {REWARDS_URL}")
        driver.get(REWARDS_URL)
        time.sleep(2) # Allow page to initially load

        # --- Attempt Login ---
        if not attempt_login(driver):
            print("Login failed. Exiting script.")
            print("Please check your credentials and the login element selectors in the script.")
            print("You may also need to handle CAPTCHAs manually if they appear.")
            return # Exit if login fails

        # Navigate to the rewards URL again after login, in case login redirected elsewhere
        print(f"Re-navigating to rewards page after login attempt: {REWARDS_URL}")
        driver.get(REWARDS_URL)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body"))) # Wait for body to ensure page is loading

        print("Waiting for the event page to fully load after login...")
        time.sleep(5) # Give some extra time for dynamic content on the event page to load

        # --- Attempt to find and click the redeem/sign-in button ---
        possible_button_xpaths = [
            "//div[contains(@class, 'signin-btn') and not(contains(@class, 'signed')) and not(contains(@class, 'disabled'))]",
            "//div[contains(@class, 'sign-btn') and not(contains(@class, 'signed')) and not(contains(@class, 'disabled'))]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in') and not(@disabled)]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'check in') and not(@disabled)]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'claim') and not(@disabled)]",
            "//div[contains(@class, 'components-pc-assets-sign-in_btn_text')]", # Specific to some HoYo events
            "//div[contains(@class, 'sign-in-btn') and not(contains(@class, 'is-signed'))]",
            "//div[contains(@class, 'mhy-hoyolab-daily-check-in') and contains(@class, 'check-in-button') and not(contains(@class, 'checked-in'))]",
            "//div[contains(@class, 'bbs-event-signin__button') and not(contains(@class, 'is-claimed'))]",
            "//div[contains(@class, 'reward-item') and contains(@class, 'available') and not(contains(@class, 'claimed'))]//div[contains(@class, 'claim-btn')]"
        ]

        redeem_button = None
        found_button_xpath = None

        for i, xpath in enumerate(possible_button_xpaths):
            try:
                print(f"\nAttempting to find redeem button with XPath ({i+1}/{len(possible_button_xpaths)}): {xpath}")
                button_candidate = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                if button_candidate.is_displayed():
                    redeem_button = button_candidate
                    found_button_xpath = xpath
                    print(f"SUCCESS: Redeem button found and clickable with XPath: {xpath}")
                    break
                else:
                    print(f"INFO: Redeem button found with XPath but not displayed: {xpath}")
            except TimeoutException:
                print(f"TIMEOUT: Redeem button not found or not clickable within 15s using XPath: {xpath}")
            except NoSuchElementException:
                print(f"NOT FOUND: Redeem button does not exist with XPath: {xpath}")
            except Exception as e:
                print(f"UNEXPECTED ERROR while searching for redeem button with XPath {xpath}: {e}")

        if redeem_button:
            try:
                print("\nAttempting to click the redeem/sign-in button...")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", redeem_button)
                time.sleep(1)
                redeem_button.click()
                print("Redeem button clicked successfully!")
                print("Please check the browser window for confirmation.")
                # Optional: Wait for success message
                # try:
                #     success_message_xpath = "//div[contains(text(), 'Successfully') or contains(text(), 'Claimed')]"
                #     success_element = WebDriverWait(driver, 10).until(
                #         EC.visibility_of_element_located((By.XPATH, success_message_xpath))
                #     )
                #     print(f"Confirmation message found: {success_element.text}")
                # except TimeoutException:
                #     print("No specific success message found, but click was attempted.")
            except Exception as e:
                print(f"ERROR clicking the redeem button (found with XPath: {found_button_xpath}): {e}")
                print("This could be due to an overlay, CAPTCHA, or other dynamic content.")
        else:
            print("-" * 50)
            print("CRITICAL: Could not find the redeem/sign-in button after login attempt.")
            print("Ensure the login was successful and you are on the correct event page.")
            print("You may need to adjust 'possible_button_xpaths' or inspect the page for the correct selector.")
            print("-" * 50)

        print("\nScript finished. Browser window will remain open for 30 seconds for you to inspect.")
        time.sleep(30)

    except TimeoutException:
        print("Page timed out while loading or a crucial element was not found in time.")
    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")
    finally:
        if 'driver' in locals() and driver is not None:
            print("Closing the browser.")
            driver.quit()

if __name__ == "__main__":
    main()
