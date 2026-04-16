from flask import Blueprint, request, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import undetected_chromedriver as uc

# Flask Blueprint for YouTube Scraper
youtube_bp = Blueprint('youtube', __name__, template_folder="templates")

# Store results
found_users = {}
screenshot_paths = {}

@youtube_bp.route('/youtube_scrape', methods=['POST'])
def youtube_scrape():
    global found_users, screenshot_paths
    found_users.clear()
    screenshot_paths.clear()

    video_url = request.form.get("video_url", "").strip()
    raw_target_names = request.form.get("target_names", "").strip()
    target_names = raw_target_names.split(",")
    tab_sleep_time = float(request.form.get("tab_sleep_time", 0.2))

    if not video_url or not raw_target_names:
        return render_template("youtube.html", error="Please fill in all fields.")

    # Normalize the target names and preserve exact names (spaces intact)
    target_names = [name.strip() for name in target_names if name.strip()]
    if not target_names:
        return render_template("youtube.html", error="Please enter at least one target username.")
    
    # Configure Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  
    driver = uc.Chrome(version_main=136, options=options, headless=False)
    
    try:
        driver.get(video_url)
        time.sleep(5)  # Let page load

        # Scroll down multiple times to load comments properly
        for _ in range(5):  # Adjust the range if needed
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(1.5)

        # Extra wait to ensure comments are fully loaded
        time.sleep(3)

        tab_count = 0

        found_any = False  # To stop when all usernames are found

        static_folder = os.path.join(os.getcwd(), "static")
        os.makedirs(static_folder, exist_ok=True)

        # Continue searching until all usernames are found
        while len(found_users) < len(target_names):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
            time.sleep(tab_sleep_time)
            tab_count += 1

            focused_element = driver.execute_script("return document.activeElement;")
            if not focused_element:
                continue  # Skip if no element is focused  

            highlighted_text = focused_element.text.strip()
            print(f"🔍 Highlighted: {highlighted_text}")

            for name in target_names:
                if name == highlighted_text:  # Exact match check
                    if name not in found_users:
                        print(f"\n✅ Found exact match for '{name}'! Preparing to tab 3 more times...\n")
                        
                        # Tab 3 more times before taking a screenshot
                        for _ in range(3):
                            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
                            time.sleep(tab_sleep_time)

                        # Now take the screenshot after tabbing 3 more times
                        print(f"\n✅ Found '{name}'! Taking screenshot...\n")
                        found_users[name] = True

                        screenshot_filename = f"{name}_screenshot.png"
                        screenshot_path = os.path.join(static_folder, screenshot_filename)
                        driver.save_screenshot(screenshot_path)
                        screenshot_paths[name] = f"/static/{screenshot_filename}"
                    
                    break  # Break after processing the found username

        print("🚀 Search finished. Found all usernames.")

    except Exception as e:
        print(f"❌ Error: {e}")
        found_users = {}
        screenshot_paths = {}

    driver.quit()
    return redirect(url_for('youtube.youtube_result'))

@youtube_bp.route('/youtube_result')
def youtube_result():
    return render_template("result.html", 
                           found_usernames=found_users, 
                           screenshot_paths=screenshot_paths, 
                           platform="YouTube")