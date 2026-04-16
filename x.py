from flask import Blueprint, request, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import undetected_chromedriver as uc

# Flask Blueprint for Twitter Scraper
twitter_bp = Blueprint('twitter', __name__, template_folder="templates")

# Store results
found_users = {}
screenshot_paths = {}

@twitter_bp.route('/twitter_scrape', methods=['POST'])
def twitter_scrape():
    global found_users, screenshot_paths
    found_users.clear()
    screenshot_paths.clear()

    tweet_url = request.form.get("tweet_url", "").strip()
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    target_usernames = request.form.get("target_usernames", "").strip().split(",")

    if not tweet_url or not username or not email or not password or not target_usernames:
        return render_template("x.html", error="Please fill in all fields.")

    target_usernames = {user.strip().lower() for user in target_usernames}  # Normalize usernames

    # Configure Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(version_main=136, options=options, headless=False)

    try:
        driver.get("https://x.com/i/flow/login")
        time.sleep(3)

        def enter_text(field_locator, value):
            """Finds an input field, clears it, and types a value (handles errors)."""
            for _ in range(3):  # Retry up to 3 times
                try:
                    field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, field_locator))
                    )
                    field.clear()
                    field.send_keys(value + Keys.RETURN)
                    time.sleep(2)
                    return True
                except Exception:
                    print(f"⚠️ Retrying input for {field_locator}...")
                    time.sleep(2)
            return False

        # **Enter Email**
        enter_text("input", email)

        # **Check if username confirmation is needed**
        try:
            username_field = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input"))
            )
            username_field.send_keys(username + Keys.RETURN)
            time.sleep(2)
        except Exception:
            print("✅ No username confirmation needed.")

        # **Ensure Password Field Exists**
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

        # **Enter Password**
        enter_text("input[name='password']", password)

        time.sleep(5)  # Wait for login to complete

        # **Navigate to Tweet**
        driver.get(tweet_url)
        time.sleep(5)

        static_folder = os.path.join(os.getcwd(), "static")
        os.makedirs(static_folder, exist_ok=True)

        found_targets = set()  # Track found usernames

        print("🚀 Starting tab navigation...\n")

        # **Ensure Page Focus**
        body = driver.find_element(By.TAG_NAME, "body")
        driver.execute_script("arguments[0].focus();", body)

        tab_count = 0
        max_tabs = 20000000

        while tab_count < max_tabs:
            try:
                # **Ensure the page is focused before pressing tab**
                driver.execute_script("arguments[0].focus();", body)

                # Simulate rapid tab presses
                webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
                time.sleep(0.05)  # Small delay for faster tabbing

                # Get the currently focused element
                focused_element = driver.execute_script("return document.activeElement;")
                if not focused_element:
                    continue

                highlighted_text = focused_element.text.strip().lower()
                print(f"🔍 Highlighted: {highlighted_text}")

                for target in target_usernames:
                    if target in highlighted_text and target not in found_targets:
                        print(f"\n✅ Found '{target}'! Taking screenshot...\n")
                        found_users[target] = True
                        found_targets.add(target)  # Mark as found

                        screenshot_filename = f"{target}_screenshot.png"
                        screenshot_path = os.path.join(static_folder, screenshot_filename)
                        driver.save_screenshot(screenshot_path)
                        screenshot_paths[target] = f"/static/{screenshot_filename}"

                tab_count += 1  # Increment tab counter

                # Stop when all usernames are found
                if found_targets == target_usernames:
                    print("\n✅✅✅ All target usernames found! Stopping tabbing...\n")
                    break

            except Exception as e:
                print(f"⚠️ Warning: Issue encountered while tabbing - {e}")
                time.sleep(0.2)  # Small delay before retrying

        print("🚀 Search finished. Tabs used:", tab_count)

    except Exception as e:
        print(f"❌ Error: {e}")
        found_users = {}
        screenshot_paths = {}

    driver.quit()
    return redirect(url_for('twitter.twitter_result'))

@twitter_bp.route('/twitter_result')
def twitter_result():
    return render_template("result.html", 
                           found_usernames=found_users, 
                           screenshot_paths=screenshot_paths, 
                           platform="Twitter/X")
