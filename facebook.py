from flask import Blueprint, request, render_template, jsonify, redirect, url_for
import os
import time
import random
import re # re module was imported but not used in the snippet, kept it in case it's used elsewhere
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

facebook_bp = Blueprint('facebook', __name__, template_folder="templates")

# Global Variables
found_usernames = {}  # Store search results
screenshot_paths = {}  # Store screenshot paths

@facebook_bp.route('/facebook_scrape', methods=['POST'])
def facebook_scrape():
    global found_usernames, screenshot_paths
    # Clear previous results at the beginning of a new scrape
    found_usernames.clear()
    screenshot_paths.clear()

    post_url = request.form.get("post_url", "").strip()
    target_usernames_input = request.form.get("target_usernames", "").strip()
    
    if not target_usernames_input: # Check if the input string is empty
        target_usernames_list = []
    else:
        target_usernames_list = target_usernames_input.split(",")
        
    tab_sleep_time = float(request.form.get("tab_sleep_time", 0.2))
    # The 'remove_safety_limit' variable was present but its corresponding 'max_tabs' logic is being removed
    # remove_safety_limit = request.form.get("safety_limit") == "off" 

    # Normalize and preserve exact usernames, including spaces
    # Ensure to filter out any empty strings that might result from split if input was just "," or had empty segments
    target_usernames = [name.strip() for name in target_usernames_list if name.strip()]


    if not post_url or not target_usernames: # Now checks if the processed list is empty
        return render_template("facebook.html", error="❌ Missing required fields. Please provide a Post URL and at least one Target Username.")

    driver = None # Initialize driver to None for the finally block
    try:
        print("Initializing Chrome driver for Facebook scrape...")
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Consider adding --no-sandbox and --disable-dev-shm-usage if running in specific environments (e.g., Docker/Linux)
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--start-maximized")
        # Add language options to try and get consistent UI from Facebook if needed
        # options.add_argument('--lang=en-US')
        # options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US,en'})

        # Ensure you have Chrome version 136 installed, or remove/adjust version_main
        driver = uc.Chrome(version_main=136, options=options, headless=False)
        print(f"Driver initialized. Navigating to Facebook post URL: {post_url}")
        driver.get(post_url)
        time.sleep(random.uniform(5, 7)) # Allow page to load

        tab_count = 0 # Initialize tab count for logging/debugging if needed

        static_folder = os.path.join(os.getcwd(), "static")
        os.makedirs(static_folder, exist_ok=True)
        print(f"Static folder for screenshots: {static_folder}")

        print(f"Starting search for {len(target_usernames)} target username(s): {', '.join(target_usernames)}")
        # Keep searching until all usernames are found (max_tabs limit removed)
        # The loop now only stops if all users are found or an error occurs, or if the browser is manually closed (implicitly)
        while len(found_usernames) < len(target_usernames):
            try:
                # Check if browser window is still open, Selenium commands will fail if it's closed
                # A simple check could be driver.title, but most commands will raise an exception
                if not driver.window_handles: # Checks if any window is open
                    print("Browser window was closed. Stopping scrape.")
                    break
                
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
            except Exception as e_tab: # Catching specific exception from tabbing if window closed
                print(f"Error during TAB key press (window might be closed): {e_tab}")
                break # Exit loop if cannot interact

            time.sleep(tab_sleep_time)
            tab_count += 1

            try:
                focused_element = driver.execute_script("return document.activeElement;")
            except Exception as e_script:
                print(f"Error getting focused element (window might be closed): {e_script}")
                break # Exit loop

            if not focused_element:
                # print(f"Tab {tab_count}: No element focused.") # Optional: for verbose logging
                continue

            highlighted_text = ""
            try:
                highlighted_text = focused_element.text.strip()
            except Exception: # StaleElementReferenceException or others
                # print(f"Tab {tab_count}: Could not get text from focused element, it might be stale.") # Optional
                continue 

            if highlighted_text: # Only print if there's actual text
                 print(f"Tab {tab_count}: Focused Text: '{highlighted_text}'")

            # Handle "view more comments" or similar buttons (case-insensitive)
            # Making these XPaths or more specific locators would be more robust
            view_more_texts = ["view more comments", "load more comments", "see more", "view previous comments", "view all replies"]
            if any(vm_text in highlighted_text.lower() for vm_text in view_more_texts):
                try:
                    print(f"Attempting to click '{highlighted_text}'...")
                    focused_element.send_keys(Keys.ENTER) # Or focused_element.click() if it's more reliable
                    time.sleep(random.uniform(2, 4)) # Wait for content to load
                    print("Clicked 'view more' type button.")
                    continue # Continue to next tab iteration to re-evaluate page
                except Exception as e_click:
                    print(f"Could not click 'view more' button: {e_click}")


            for username_to_find in target_usernames:
                # Check if this username has already been found
                if username_to_find in found_usernames:
                    continue

                # Use exact match for finding and screenshotting
                if highlighted_text == username_to_find:
                    print(f"✅ Found exact match for username: {username_to_find}")
                    
                    found_usernames[username_to_find] = True # Mark as found with True

                    screenshot_filename = f"{username_to_find.replace(' ', '_')}_screenshot.png" # Sanitize filename
                    screenshot_path = os.path.join(static_folder, screenshot_filename)
                    
                    try:
                        driver.save_screenshot(screenshot_path)
                        screenshot_paths[username_to_find] = f"/static/{screenshot_filename}"
                        print(f"📸 Screenshot saved for {username_to_find}: {screenshot_path}")
                    except Exception as e_screenshot:
                        print(f"❌ Failed to save screenshot for {username_to_find}: {e_screenshot}")
                    
                    # No 'break' here, let it finish checking other usernames against this highlighted_text
                    # if multiple target usernames could be the same as highlighted_text (unlikely for exact match)
                    # However, if a username is unique, finding it means we can move to the next TAB more quickly.
                    # If one highlighted_text can only match one username, then break makes sense.
                    # Given highlighted_text == username_to_find, a break is fine.
                    break 
            
            # Safety break for extremely long pages / unexpected loops - consider re-adding if needed for dev
            # if tab_count > SOME_VERY_LARGE_NUMBER_LIKE_10000 and remove_safety_limit is False:
            # print("Reached a high tab count without finding all users, stopping to prevent infinite loop.")
            # break

        if len(found_usernames) == len(target_usernames):
            print("🚀 All target usernames found.")
        else:
            print(f"⚠️ Search finished. Found {len(found_usernames)} out of {len(target_usernames)} target usernames. Tab count: {tab_count}")

    except WebDriverException as e_wd:
        print(f"❌ WebDriverException occurred: {e_wd}. This might be due to browser closing or driver issues.")
        # Globals are cleared again here just in case of partial success before error
        found_usernames.clear()
        screenshot_paths.clear()
    except Exception as e:
        print(f"❌ An unexpected error occurred during scraping: {e}")
        import traceback
        traceback.print_exc()
        found_usernames.clear()
        screenshot_paths.clear()
    finally:
        if driver:
            print("Attempting to quit driver...")
            driver.quit()
            print("Driver quit.")

    print("🔄 Redirecting to results page...")
    return redirect(url_for('facebook.facebook_result'))

@facebook_bp.route('/facebook_result')
def facebook_result():
    print(f"Rendering result.html with {len(found_usernames)} found users.")
    # Pass a copy or ensure data is as expected
    return render_template("result.html", 
                           found_usernames=dict(found_usernames), 
                           screenshot_paths=dict(screenshot_paths), 
                           platform="facebook")