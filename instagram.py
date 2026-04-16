from flask import Blueprint, request, render_template
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

instagram_bp = Blueprint('instagram', __name__, template_folder="templates")

@instagram_bp.route('/instagram_scrape', methods=['POST'])
def instagram_scrape():
    ig_email = request.form.get("ig_email")
    ig_password = request.form.get("ig_password")
    post_url = request.form.get("post_url")
    target_usernames_str = request.form.get("target_usernames")
    safety_switch = request.form.get("safety_switch")
    tab_sleep_time = float(request.form.get("tab_sleep_time", 0.1))

    target_list = [username.strip() for username in target_usernames_str.split(",") if username.strip()]
    found_usernames = {username: False for username in target_list}
    screenshot_paths = {}

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(version_main=136, options=options, headless=False)

    try:
        driver.get("https://www.instagram.com")
        time.sleep(5)
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))

        email_input.send_keys(ig_email)
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(ig_password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

        try:
            not_now_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Not Now']")))
            not_now_button.click()
            time.sleep(3)
        except Exception:
            pass

        driver.get(post_url)
        time.sleep(5)

        static_folder = os.path.join(os.getcwd(), "static")
        os.makedirs(static_folder, exist_ok=True)

        tab_count = 0

        while not all(found_usernames.values()):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
            time.sleep(tab_sleep_time)
            tab_count += 1

            highlighted_text = driver.execute_script("return document.activeElement.textContent;").strip()

            for username in target_list:
                if not found_usernames[username] and highlighted_text == username:
                    found_usernames[username] = True
                    
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
                    time.sleep(tab_sleep_time)

                    screenshot_filename = f"instagram_screenshot_{username}.png"
                    screenshot_path = os.path.join(static_folder, screenshot_filename)
                    driver.save_screenshot(screenshot_path)
                    screenshot_paths[username] = "/static/" + screenshot_filename

            if not all(found_usernames.values()):
                try:
                    load_more = driver.find_element(By.XPATH, "//svg[@aria-label='Load more comments']")
                    driver.execute_script("arguments[0].click();", load_more)
                    time.sleep(2)
                except Exception:
                    pass

    except Exception as e:
        print(f"Error: {e}")

    return render_template("result.html", screenshot_paths=screenshot_paths,
                           found_usernames=found_usernames, platform="instagram")
