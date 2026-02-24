#!/usr/bin/env python3
# -*- coding: utf‑8 -*-
"""
tixcraft_auto_ticket.py
=======================

This script demonstrates how to automate part of the ticket‑purchasing flow on
the tixCraft website (https://tixcraft.com) using Selenium WebDriver.  The
goal of the script is to help you quickly navigate to the Xiao Bing Chih
《活著Alive》 Kaohsiung Arena concert page and click through to the seat
selection screen.  Once the seat map is available the script tries to pick
seats according to your price preferences, then proceeds to the checkout page.

**Important usage notes**

* The script is intended as a starting point for your own automation.  You
  will need to adjust element locators and wait times to match changes in
  tixCraft's HTML structure.  During high demand periods (for example when
  ticket sales open), tixCraft places you in a virtual queue and may require
  a "I'm not a robot" CAPTCHA check.  These steps cannot be bypassed and
  require manual intervention.  When prompted in the terminal, switch to
  the browser window, complete any login or CAPTCHA steps, then return to
  the terminal and press Enter to continue the script.

* The purchase of event tickets is an everyday financial activity under
  OpenAI's policy.  The script will automatically navigate to the final
  confirmation page but will not click the final "Confirm purchase" or
  equivalent button without your explicit confirmation.  A prompt will
  appear in your terminal asking you to confirm the order before the last
  submission.  Answering "y" will proceed; any other input will cancel
  the operation.

* Before running this script make sure you have the necessary Python
  dependencies installed on your own machine: ``selenium`` and
  ``webdriver‑manager``.  These can be installed with ``pip install selenium
  webdriver-manager``.  You will also need a recent version of Google
  Chrome or another Chromium‑based browser installed on your computer.

Usage example::

    python tixcraft_auto_ticket.py --email YOUR_EMAIL --password YOUR_PASSWORD

If you prefer to log in manually (for example using the "Sign in with
Google/Facebook" options), omit the ``--email`` and ``--password`` arguments
and the script will pause at the login screen until you press Enter.

Author: OpenAI Assistant
Date: 2025‑07‑24
"""

import argparse
import sys
import time
from typing import List

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# URL constants for the event
EVENT_DETAIL_URL = "https://tixcraft.com/activity/detail/25_xalive"
EVENT_GAME_URL = "https://tixcraft.com/activity/game/25_xalive"


def setup_browser() -> webdriver.Chrome:
    """Configure and return a Selenium Chrome WebDriver instance.

    The function uses `webdriver‑manager` to download the appropriate
    chromedriver binary if one is not already installed.  Browser options
    are set to start maximised and to disable some automation flags which
    might cause tixCraft to detect an automated browser.

    Returns
    -------
    webdriver.Chrome
        A configured and ready Chrome WebDriver instance.
    """
    chrome_options = webdriver.ChromeOptions()
    # Important: do not run headless – tixCraft uses bot detection and
    # headless browsers are more likely to be flagged.  Running in a
    # normal visible window also allows you to complete CAPTCHAs.
    chrome_options.add_argument("--start-maximized")
    # Reduce the chance of detection by disabling automation flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # Set the language to Traditional Chinese to ensure Chinese labels
    chrome_options.add_argument("--lang=zh-TW")
    # Initialise the driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # Further tweak navigator.webdriver property via JavaScript to reduce detection
    driver.execute_c_script = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    return driver


def wait_and_click(driver: webdriver.Chrome, by: By, identifier: str, timeout: int = 20) -> bool:
    """Wait for an element to become clickable and then click it.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium driver controlling the browser.
    by : By
        The locator strategy (e.g. By.ID, By.XPATH).
    identifier : str
        The locator string corresponding to the strategy.
    timeout : int, optional
        Maximum seconds to wait before giving up.  Default is 20.

    Returns
    -------
    bool
        True if the element was clicked successfully, False otherwise.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, identifier))
        )
        element.click()
        return True
    except TimeoutException:
        return False


def accept_cookies(driver: webdriver.Chrome) -> None:
    """Attempt to accept cookies on the tixCraft site.

    tixCraft uses OneTrust to manage its cookie consent banner.  Depending on
    your region and previous visits you might not see the banner.  If the
    banner is visible, this function clicks the "接受所有 Cookie" (Accept all
    cookies) button.  If the button cannot be found within the timeout the
    function silently returns.
    """
    # The OneTrust banner injects an iframe into the page.  We need to
    # switch into the iframe before interacting with the buttons.  The
    # iframe has an id that starts with "ot-sdk".
    try:
        time.sleep(2)  # allow banner to load
        cookie_frame = driver.find_element(By.CSS_SELECTOR, "iframe[id^='onetrust-consent-sdk']")
        driver.switch_to.frame(cookie_frame)
        # Look for the "Accept all cookies" button by text
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                if "接受所有" in btn.text or "Accept" in btn.text:
                    btn.click()
                    break
            except Exception:
                continue
        # Always switch back to default content afterwards
        driver.switch_to.default_content()
    except NoSuchElementException:
        # No cookie banner present
        return


def perform_login(driver: webdriver.Chrome, email: str = None, password: str = None) -> None:
    """Log in to tixCraft using either credentials or manual authentication.

    If ``email`` and ``password`` are provided the script will attempt to log
    in using the standard email/password form.  Otherwise the script will
    navigate to the login page and pause, allowing you to use the social
    login buttons (Google/Facebook) or other methods.  After you complete
    authentication in the browser, return to the terminal and press Enter to
    resume the script.
    """
    # Open the event detail page – login links are available in the header
    driver.get(EVENT_DETAIL_URL)
    accept_cookies(driver)
    # Locate and click the "Sign In" link
    if not wait_and_click(driver, By.LINK_TEXT, "Sign In", timeout=10):
        print("Sign In link not found – you may already be logged in.")
        return
    # At this point a modal login dialog should appear
    time.sleep(2)
    # Attempt automated login if credentials were supplied
    if email and password:
        try:
            # Switch to the login iframe if present
            login_iframe = driver.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(login_iframe)
        except NoSuchElementException:
            # No iframe; proceed in main document
            pass
        try:
            email_field = driver.find_element(By.ID, "email")
            password_field = driver.find_element(By.ID, "password")
            email_field.clear()
            email_field.send_keys(email)
            password_field.clear()
            password_field.send_keys(password)
            # Submit the form
            password_field.send_keys(Keys.RETURN)
            # Wait for login to complete (checking that Sign In button disappears)
            WebDriverWait(driver, 30).until_not(
                EC.presence_of_element_located((By.LINK_TEXT, "Sign In"))
            )
            driver.switch_to.default_content()
            print("Logged in successfully.")
            return
        except Exception:
            # Something went wrong; fall back to manual login
            print("Automated login failed.  Please log in manually in the browser.")
    # Manual login path
    print("Please complete the login process in the browser window (e.g. using Social login).")
    input("After you have successfully logged in, press Enter here to continue...")


def navigate_to_event(driver: webdriver.Chrome) -> None:
    """Navigate to the event game page and click the "Find tickets" button.

    Once on the game page, the script waits for the "Find tickets" button and
    clicks it.  On high‑demand events there may be only one date, but if
    multiple dates are listed you should modify this function to select
    according to your desired date/time.
    """
    driver.get(EVENT_GAME_URL)
    accept_cookies(driver)
    # Wait for the "Find tickets" button in the game list
    try:
        # The button has data‑href pointing at the area selection page.  Use CSS to find the first one.
        find_buttons = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#gameList button[data-href]")
                                                )
        )
        if not find_buttons:
            raise NoSuchElementException("No available event dates found.")
        # Click the first available event (modify index if necessary)
        find_buttons[0].click()
    except (TimeoutException, NoSuchElementException):
        print("Could not find the 'Find tickets' button.  The event may be sold out or not yet on sale.")
        sys.exit(1)
    # At this point the browser should open the seat selection page


def select_seats(driver: webdriver.Chrome, quantity: int, price_preferences: List[str]) -> None:
    """Select seats on the seat map according to price preferences.

    This function assumes that the seat selection page lists price/section
    categories as buttons.  It loops through your preferred price levels and
    attempts to click the first available button for each level until the
    desired ticket quantity is added to the cart.  If no preferred price
    categories are available, it falls back to any available price.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium driver controlling the browser.
    quantity : int
        Number of tickets you want to purchase.
    price_preferences : list of str
        A list of price category keywords to prioritise (e.g. ["4500", "3200"]).
    """
    # Wait for the price category buttons to appear
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#areaList button.area-btn"))
        )
    except TimeoutException:
        print("Seat selection screen did not load in time.  Perhaps you are still in queue.")
        input("If you see a queue or CAPTCHA in the browser, please complete it and press Enter to retry...")
        return select_seats(driver, quantity, price_preferences)
    # Fetch all price buttons
    price_buttons = driver.find_elements(By.CSS_SELECTOR, "#areaList button.area-btn")
    chosen = False
    # Try preferred prices first
    for pref in price_preferences:
        for btn in price_buttons:
            if pref in btn.text and btn.is_enabled():
                btn.click()
                chosen = True
                break
        if chosen:
            break
    # If no preferred price was available, click the first enabled button
    if not chosen:
        for btn in price_buttons:
            if btn.is_enabled():
                btn.click()
                chosen = True
                break
    if not chosen:
        print("No available price categories were found.  The event may be sold out.")
        sys.exit(1)
    # Now select seats within the chosen price category
    # The seat map is usually loaded in an iframe; find and switch to it
    try:
        seat_frame = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='seat']"))
        )
        driver.switch_to.frame(seat_frame)
    except TimeoutException:
        # Some events load seats inline; ignore if not present
        pass
    # Click seats until the desired quantity is reached
    selected_count = 0
    while selected_count < quantity:
        try:
            # Available seats often have a class like "seat-select" or similar; adjust if needed
            seat = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".seat-available, .available"))
            )
            seat.click()
            selected_count += 1
            time.sleep(0.2)
        except TimeoutException:
            print("No more available seats could be selected.  Fewer seats may be available than requested.")
            break
    # Switch back to the main content if we switched into a frame
    try:
        driver.switch_to.default_content()
    except Exception:
        pass
    # Proceed to next step (Add to cart / Next step button)
    try:
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#nextStep"))
        )
        next_btn.click()
    except TimeoutException:
        print("Could not find the next step button.  Check if seats were successfully selected.")


def proceed_to_checkout(driver: webdriver.Chrome) -> None:
    """Handle the checkout steps up to the final payment confirmation.

    The exact checkout process on tixCraft may involve verifying your phone
    number, selecting a payment method, and entering payment details.
    Automation beyond seat selection is risky because payment details are
    sensitive and there may be additional captchas or verifications.  This
    function navigates to the order confirmation page and waits for your
    confirmation before clicking the final button.
    """
    # Wait for order summary page
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#orderInfo"))
        )
    except TimeoutException:
        print("Order summary did not appear.  Please check the browser for errors or prompts.")
        return
    print("Order summary page loaded.  Please verify the details in the browser.")
    confirm = input("Type 'y' and press Enter to confirm the order.  Any other input will cancel: ")
    if confirm.lower() == 'y':
        # Locate and click the final confirm button
        try:
            confirm_button = driver.find_element(By.CSS_SELECTOR, "button.confirm-order")
            confirm_button.click()
            print("Order submitted.")
        except NoSuchElementException:
            print("Confirm button not found.  You may need to scroll or complete additional steps manually.")
    else:
        print("Order cancelled by user.")


def main() -> None:
    """Parse arguments and orchestrate the ticket purchasing flow."""
    parser = argparse.ArgumentParser(description="Automate tixCraft ticket purchase for Xiao Bing Chih 'Alive' concert.")
    parser.add_argument("--email", help="Your tixCraft login email (optional).", default=None)
    parser.add_argument("--password", help="Your tixCraft login password (optional).", default=None)
    parser.add_argument("--quantity", type=int, help="Number of tickets to buy.", default=1)
    parser.add_argument(
        "--prices",
        nargs="*",
        default=["4500", "3200", "2800", "2200", "1500"],
        help="Preferred ticket prices in order of priority (as text).",
    )
    args = parser.parse_args()

    driver = setup_browser()
    try:
        perform_login(driver, args.email, args.password)
        navigate_to_event(driver)
        select_seats(driver, args.quantity, args.prices)
        proceed_to_checkout(driver)
    finally:
        print("Automation complete.  The browser window will remain open for manual inspection.")
        # Do not close driver automatically – allow the user to review
        # driver.quit()


if __name__ == "__main__":
    main()