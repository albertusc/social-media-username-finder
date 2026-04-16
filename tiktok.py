from flask import Blueprint, request, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

# Flask Blueprint for TikTok Scraper
tiktok_bp = Blueprint('tiktok', __name__, template_folder="templates")

# Store results
found_users = {}
screenshot_paths = {}

@tiktok_bp.route('/tiktok_scrape', methods=['POST'])
def tiktok_scrape():
    global found_users, screenshot_paths
    found_users.clear()
    screenshot_paths.clear()

    video_url = request.form.get("video_url", "").strip()
    raw_target_names = request.form.get("target_names", "").strip()
    target_names = raw_target_names.split(",")
    tab_sleep_time = float(request.form.get("tab_sleep_time", 0.2))

    if not video_url or not raw_target_names:
        return render_template("tiktok.html", error="Please fill in all fields.")

    target_names = [name.strip() for name in target_names if name.strip()]
    if not target_names:
        return render_template("tiktok.html", error="Please enter at least one target username.")
    
    # Configure Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(video_url)
        time.sleep(5)  # Allow page to load

        # Scroll down to load comments
        for _ in range(5):  # Adjust this number if needed
            driver.execute_script("window.scrollBy(0, 500);")  # Scroll down
            time.sleep(1)  # Allow comments to load

        tab_count = 0
        found_count = 0  

        static_folder = os.path.join(os.getcwd(), "static")
        os.makedirs(static_folder, exist_ok=True)

        while found_count < len(target_names):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
            time.sleep(tab_sleep_time)
            tab_count += 1

            focused_element = driver.execute_script("return document.activeElement;")
            if not focused_element:
                continue  

            highlighted_text = focused_element.text.strip()
            print(f"🔍 Highlighted: {highlighted_text}")

            for name in target_names:
                # Ensure exact match of the username
                if highlighted_text == name and name not in found_users:
                    print(f"\n✅ Found '{name}'!\n")
                    
                    # Tab one more time before screenshot
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
                    time.sleep(0.2)  # Small delay for visibility

                    # Take screenshot
                    screenshot_filename = f"{name}_screenshot.png"
                    screenshot_path = os.path.join(static_folder, screenshot_filename)
                    driver.save_screenshot(screenshot_path)
                    screenshot_paths[name] = f"/static/{screenshot_filename}"
                    
                    found_users[name] = True
                    found_count += 1  # Increase found counter
                    break  # No need to check further usernames for this tab

        print("🚀 Search finished.")

    except Exception as e:
        print(f"❌ Error: {e}")
        found_users = {}
        screenshot_paths = {}

    driver.quit()
    return redirect(url_for('tiktok.tiktok_result'))

@tiktok_bp.route('/tiktok_result')
def tiktok_result():
    return render_template("result.html", 
                           found_usernames=found_users, 
                           screenshot_paths=screenshot_paths, 
                           platform="TikTok")
