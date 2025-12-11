#!/usr/bin/env python3
import time
import logging
import re
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
    original_window = driver.current_window_handle
    try:
        
        try:
            link_tag = card_element.find_element(By.TAG_NAME, "a")
            href = link_tag.get_attribute("href")
            if href and "http" in href and "#" not in href:
                return href
        except:
            pass

        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card_element)
        time.sleep(0.5)

        actions = ActionChains(driver)
        modifier_key = Keys.COMMAND if 'mac' in driver.capabilities['platformName'].lower() else Keys.CONTROL
        
        actions.key_down(modifier_key).click(card_element).key_up(modifier_key).perform()
        
        WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
        
        windows = driver.window_handles
        new_window = [w for w in windows if w != original_window][0]
        driver.switch_to.window(new_window)
        
        WebDriverWait(driver, 5).until(lambda d: d.current_url != "about:blank")
        actual_url = driver.current_url
        
        driver.close()
        driver.switch_to.window(original_window)
        return actual_url

    except Exception:
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
            logging.info(f"--- Processing Page {page_num}/{max_pages} ---")
            
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'hover:shadow-lg')]"))
                )
            except:
                logging.warning("No cards found. Stopping.")
                break

            
            card_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'hover:shadow-lg') and contains(@class, 'cursor-pointer')]")
            logging.info(f"Found {len(card_elements)} cards on page {page_num}")

            
            for i, card in enumerate(card_elements):

                time.sleep(0.5) 
                try:
                    card_html = card.get_attribute('outerHTML')
                    soup = BeautifulSoup(card_html, "html.parser")
                    
                    title_tag = soup.find(class_=re.compile(r"font-bold"))
                    title = title_tag.get_text(strip=True) if title_tag else "No Title"
                    
                    deadline = "Not specified"
                    dl_node = soup.find(string=re.compile(r"Deadline", re.I))
                    if dl_node:
                        deadline = dl_node.parent.get_text(strip=True).replace("Deadline:", "").strip()

                    link = get_actual_url_via_click(driver, card)
                    
                    if link not in seen_urls and "Error" not in link:
                        job_data = {
                            "title": title,
                            "deadline": deadline,
                            "link": link,
                            "page": page_num
                        }
                        all_jobs.append(job_data)
                        seen_urls.add(link)
                        #logging.info(f"Parsed: {title[:30]}... -> {link}")
                    
                except Exception as e:
                    logging.error(f"Error parsing card {i}: {e}")
                    continue

            #Handle Pagination 
            if page_num < max_pages:
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)


                    next_btn = driver.find_element(
                        By.XPATH,
                        "//div[contains(@class, 'cursor-pointer')][.//div[text()='Next']]"
                    )

                    logging.info("Clicking Next Page...")
                    driver.execute_script("arguments[0].click();", next_btn)
                    

                    time.sleep(4)
                except Exception as e:
                    logging.info(f"Next button not found or error: {e}")
                    break
            else:
                logging.info(f"Reached limit of {max_pages} pages. Stopping.")

    finally:
        driver.quit()
    
    return all_jobs

if __name__ == "__main__":
    scrape_shomvob_pagination(max_pages=3)