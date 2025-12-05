#!/usr/bin/env python3
import time
import json
import logging
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")

BASE_URL = "https://app.shomvob.co/all-jobs/"

def setup_driver(headless=True):
    """
    Headless is FALSE by default so you can see it working.
    Set to TRUE if running on a server.
    """
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    return driver

def get_actual_url_via_click(driver, card_element):
    """
    Opens the card in a new tab to grab the URL without losing pagination state.
    """
    original_window = driver.current_window_handle
    
    try:
        # Attempt 1: Look for an anchor tag inside the card first (Faster)
        # Try finding the "Details" button or any <a> with href
        try:
            link_tag = card_element.find_element(By.TAG_NAME, "a")
            href = link_tag.get_attribute("href")
            if href and "http" in href and "#" not in href:
                return href
        except:
            pass

        # Attempt 2: CTRL + Click the card (Reliable for JS links)
        # Scroll to element to ensure it's clickable
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card_element)
        time.sleep(0.5)

        # Perform CTRL+Click (Cmd+Click on Mac)
        actions = ActionChains(driver)
        modifier_key = Keys.COMMAND if 'mac' in driver.capabilities['platformName'].lower() else Keys.CONTROL
        
        actions.key_down(modifier_key).click(card_element).key_up(modifier_key).perform()
        
        # Wait for new tab to open
        WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
        
        # Switch to new tab
        windows = driver.window_handles
        new_window = [w for w in windows if w != original_window][0]
        driver.switch_to.window(new_window)
        
        # Wait for URL to stabilize (non-empty)
        WebDriverWait(driver, 5).until(lambda d: d.current_url != "about:blank")
        actual_url = driver.current_url
        
        # Close tab and return
        driver.close()
        driver.switch_to.window(original_window)
        return actual_url

    except Exception as e:
        # If anything fails, ensure we are back on the main window
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(original_window)
        return "Error extracting link"

def scrape_shomvob_pagination(max_pages=3, out_file="BRAC_Project/Job_Post_Scrapping/Shomvob/links.json"):
    driver = setup_driver(headless=True)
    all_jobs = []
    seen_urls = set()

    try:
        logging.info(f"Navigating to {BASE_URL}")
        driver.get(BASE_URL)
        time.sleep(3)

        for page_num in range(1, max_pages + 1):
            logging.info(f"--- Processing Page {page_num} ---")
            
            # 1. Wait for cards to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'hover:shadow-lg')]"))
                )
            except:
                logging.warning("No cards found on this page. Stopping.")
                break

            # 2. Find all card elements (Selenium WebElements)
            # Using the selector from your screenshot: divs with hover:shadow-lg and cursor-pointer
            card_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'hover:shadow-lg') and contains(@class, 'cursor-pointer')]")
            logging.info(f"Found {len(card_elements)} cards on page {page_num}")

            page_job_count = 0
            
            # 3. Iterate through cards
            for i, card in enumerate(card_elements):
                
                time.sleep(2)
                try:
                    # Extract text using BS4 for speed/safety on the static content
                    card_html = card.get_attribute('outerHTML')
                    soup = BeautifulSoup(card_html, "html.parser")
                    
                    # Title: Bold text
                    title_tag = soup.find(class_=re.compile(r"font-bold"))
                    title = title_tag.get_text(strip=True) if title_tag else "No Title"
                    
                    # Deadline: Text containing 'Deadline'
                    deadline = "Not specified"
                    dl_node = soup.find(string=re.compile(r"Deadline", re.I))
                    if dl_node:
                        deadline = dl_node.parent.get_text(strip=True).replace("Deadline:", "").strip()

                    # --- CRITICAL: GET LINK ---
                    # We pass the Selenium 'card' object to our click helper
                    link = get_actual_url_via_click(driver, card)
                    
                    if link not in seen_urls:
                        job_data = {
                            "title": title,
                            "deadline": deadline,
                            "link": link,
                            "page": page_num
                        }
                        all_jobs.append(job_data)
                        seen_urls.add(link)
                        page_job_count += 1
                        logging.info(f"Parsed: {title[:30]}... -> {link}")
                    
                except Exception as e:
                    logging.error(f"Error parsing card {i}: {e}")
                    continue

            try:
                # Scroll to bottom (this activates the pagination component)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Wait until the Next button becomes interactable
                next_btn = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'cursor-pointer')][.//div[text()='Next']]"
                )

                logging.info("Clicking Next Page...")

                # Use JS click (normal Selenium click does NOT work here)
                driver.execute_script("arguments[0].click();", next_btn)

                time.sleep(3)  # Wait for React to load new page

            except Exception as e:
                logging.info(f"Reached last page or Next not clickable: {e}")
                break
            break
        # Save Data
        #with open(out_file, "w", encoding="utf-8") as f:
        #    json.dump(all_jobs, f, indent=4, ensure_ascii=False)
        #logging.info(f"Saved {len(all_jobs)} jobs to {out_file}")
        
    
    finally:
        driver.quit()
    return all_jobs

if __name__ == "__main__":
    
    scrape_shomvob_pagination(max_pages=3)