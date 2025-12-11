import time
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Helper Function to Correctly Scrape Lists ---
def extract_list_items(driver, parent_xpath):
    """
    Finds a parent element (like a <ul>) and extracts the text of each 
    child <li> element into a Python list.
    Returns an empty list if not found.
    """
    try:
        # Find all the <li> elements within the parent
        list_elements = driver.find_elements(By.XPATH, f"{parent_xpath}//li")
        # Return a list of their text, stripping any extra whitespace
        return [item.text.strip() for item in list_elements if item.text.strip()]
    except NoSuchElementException:
        return []

# --- 1. Setup Headless Browser and Anti-Detection Options ---
def setup_driver():
    options = Options()
    options.add_argument("--headless=new")  # Updated headless argument
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver



def scrape_details_memory(links):
    driver = setup_driver()
    all_job_details = []

    # --- 3. Loop Through Links and Scrape Details ---
    for i, job in enumerate(links):
        url = job
        url = job.get('link')
        if not url:
            continue

        print(f"Scraping link {i+1}/{len(links)}: {url}")
        
        driver.get(url)
        
        try:
            
            wait = WebDriverWait(driver,30) 
            wait.until(EC.visibility_of_element_located(((By.ID, "sum"))))
            
            # --- Data Extraction ---

            responsibilities = extract_list_items(driver, "//*[@id='responsibilitiesSection']")
            education = extract_list_items(driver, "//*[@id='requirements']/div[1]")
            experience = extract_list_items(driver, "//*[@id='requirements']/div[2]")
            add_req = extract_list_items(driver, "//*[@id='requirements']/div[3]")
            other_benefits = extract_list_items(driver, "//*[@id='salary']")
            

            try:
                vacancy = driver.find_element(By.XPATH, "//strong[contains(text(), 'Vacancy')]/following-sibling::span").text
            except NoSuchElementException:
                vacancy = "Not specified"
            try:
                company_name = driver.find_element(By.XPATH, "/html/body/app-root/app-layout/div[2]/app-job-details/div/div/div[1]/div/div[1]/div/div/div[1]/div/div/h2[1]").text
            except:
                company_name = "Not found"
            try:
                skills_container = driver.find_element(By.XPATH, "//*[@id='skills']/div")
                skills = [skill.strip() for skill in skills_container.text.split('\n') if skill.strip()]
            except NoSuchElementException:
                skills = []
            

            try:
                employment_status = driver.find_element(By.XPATH, '/html/body/app-root/app-layout/div[2]/app-job-details/div/div/div[1]/div/div[1]/div/div/div[6]/div[3]/div/div/div[4]').text.split("\n")[1]

            except NoSuchElementException:
                employment_status = "Not found"
            

            published, age, salary, location = "Not found", "Not found", "Not found", "Not found"
            info_elements = driver.find_elements(By.XPATH, '//*[@id="allSection"]/ul/div')
            for info_text in [element.text for element in info_elements]:
                text_lower = info_text.lower()
                if "published" in text_lower:
                    published = info_text.replace("Published:", "").strip()
                elif "age" in text_lower:
                    age = info_text.replace("Age:", "").strip()
                elif "salary" in text_lower:
                    salary = info_text.replace("Salary:", "").strip()
                elif "location" in text_lower:
                    location = info_text.replace("location:", "").strip()

            # Combine all data
            job_data = {
                'title': job.get('title'),
                'company_name': company_name,
                'deadline': job.get('deadline'),
                'url': url,
                'responsibilities': responsibilities,
                'employment_status': employment_status.strip(),
                'education': education,
                'experience': experience,
                'additional_requirements': add_req,
                'vacancy': vacancy.strip(),
                'location': location.strip(),
                'age': age.strip(),
                'salary': salary.strip(),
                'other_benefits': other_benefits,
                'published': published.strip(),
                'skills': skills,
            }
            all_job_details.append(job_data)
            

            time.sleep(random.uniform(6, 13))

        except (TimeoutException, Exception) as e:
            print(f"Could not process {url}. Error: {e}")

    
    driver.quit()
    return all_job_details