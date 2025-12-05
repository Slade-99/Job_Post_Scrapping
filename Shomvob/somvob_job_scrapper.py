import time
import json
import random
import logging
from datetime import datetime  # Added for current date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# --- CONFIGURATION ---
INPUT_FILE = 'BRAC_Project/Job_Post_Scrapping/Shomvob/filtered.json' 
OUTPUT_FILE = 'BRAC_Project/Job_Post_Scrapping/Shomvob/shomvob_job_details.json'

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")

def setup_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--headless=new") 
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=opts)
    return driver

def extract_json_ld(soup):
    """Extracts the hidden JSON-LD schema."""
    try:
        script = soup.find('script', type='application/ld+json')
        if script:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'JobPosting':
                        return item
            elif data.get('@type') == 'JobPosting':
                return data
    except Exception as e:
        pass
    return {}

def get_visual_grid_data(soup, label):
    """Finds a label in the grid and gets the sibling text."""
    try:
        label_div = soup.find(lambda tag: tag.name == "div" and tag.get_text(strip=True) == label)
        if label_div:
            value_div = label_div.find_next_sibling("div")
            if value_div:
                return value_div.get_text(strip=True)
    except:
        pass
    return "Not found"

def clean_html_to_list(html_content):
    """Converts HTML to clean list."""
    if not html_content:
        return []
    
    # Pre-process to ensure lines split correctly
    html_content = str(html_content).replace("<br>", "\n").replace("<br/>", "\n").replace("</p>", "\n")
    soup = BeautifulSoup(html_content, "html.parser")
    items = []
    
    # 1. Try finding list items <li>
    li_tags = soup.find_all('li')
    if li_tags:
        for li in li_tags:
            text = li.get_text(strip=True)
            if text: items.append(text)
    else:
        # 2. Split paragraph text by newlines
        text_block = soup.get_text("\n")
        items = [line.strip() for line in text_block.split('\n') if len(line.strip()) > 2]

    return items

def get_salary_visual(soup):
    """Fallback to find salary visually using Regex."""
    try:
        salary_node = soup.find(string=re.compile(r"(TK\.|Tk\.|৳|Salary)", re.I))
        if salary_node:
            return salary_node.parent.get_text(strip=True)
    except:
        pass
    return "Negotiable"

def get_company_visual(soup):
    """Robust fallback for company name."""
    try:
        # 1. Try the Logo Alt Text (Most reliable on Shomvob)
        logo = soup.find("img", class_=lambda x: x and "object-contain" in x)
        if logo and logo.get("alt"):
            return logo.get("alt")
            
        # 2. Try text under title (Secondary color text)
        # Find the Job Title first (usually bold and large)
        title_node = soup.find("div", class_=re.compile(r"font-bold"))
        if title_node:
            # The company is usually the next div with 'Secondary' text color
            company_node = title_node.find_next("div", class_=re.compile(r"Text-Secondary"))
            if company_node:
                return company_node.get_text(strip=True)
    except:
        pass
    return "Not specified"

def scrape_details():
    driver = setup_driver()
    all_job_data = []

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            jobs_to_scrape = json.load(f)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"loaded {len(jobs_to_scrape)} links. Starting scrape...")

    for i, job_entry in enumerate(jobs_to_scrape):
        url = job_entry.get('link') or job_entry.get('url')
        if not url: continue

        print(f"[{i+1}/{len(jobs_to_scrape)}] Processing: {url}")
        
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2) 

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            schema = extract_json_ld(soup)
            
            # --- Visual Grid Helpers ---
            grid_vacancy = get_visual_grid_data(soup, "Vacancy")
            grid_experience = get_visual_grid_data(soup, "Experience")
            grid_education = get_visual_grid_data(soup, "Education")
            
            # --- 1. Published Date (Todays Date) ---
            published_raw = datetime.now().strftime("%d %b %Y")

            # --- 2. Responsibilities Logic (Fixed) ---
            responsibilities_list = []
            
            # Try Schema first
            resp_html = schema.get('responsibilities', '') 
            if not resp_html: 
                resp_html = schema.get('description', '')
            
            if resp_html:
                responsibilities_list = clean_html_to_list(resp_html)
            
            # If still empty, try Visual Search for "Responsibilities" header
            if not responsibilities_list:
                try:
                    resp_header = soup.find(lambda tag: tag.name == "div" and "Responsibilities" in tag.get_text())
                    if resp_header:
                        # The content is usually in the next sibling div
                        content_div = resp_header.find_next_sibling("div")
                        if not content_div: # Sometimes it's inside a parent container structure
                            content_div = resp_header.parent.find_next_sibling("div")
                        if content_div:
                            responsibilities_list = clean_html_to_list(str(content_div))
                except: pass

            # --- 3. Company Logic (Fixed) ---
            company = schema.get('hiringOrganization', {}).get('name')
            # If schema misses it or gives generic name, use visual extraction
            if not company or company.lower() == "shomvob": 
                company = get_company_visual(soup)

            # --- 4. Salary Logic ---
            salary = "Negotiable"
            if schema.get('baseSalary'):
                try:
                    val = schema['baseSalary'].get('value', {})
                    min_s = val.get('minValue') or schema['baseSalary'].get('minValue')
                    max_s = val.get('maxValue') or schema['baseSalary'].get('maxValue')
                    if min_s:
                        salary = f"Tk. {min_s}" + (f" - {max_s}" if max_s else "") + " (Monthly)"
                except: pass
            
            if salary == "Negotiable":
                vis_sal = get_salary_visual(soup)
                if vis_sal: salary = vis_sal

            # --- Benefits ---
            benefits_list = schema.get('jobBenefits', [])
            if not benefits_list:
                ben_header = soup.find(string=re.compile("Benefits"))
                if ben_header:
                    try:
                        parent = ben_header.find_parent("div").find_parent("div")
                        benefits_list = [li.get_text(strip=True) for li in parent.find_all("div", class_="flex") if li.get_text(strip=True) and "Benefits" not in li.get_text(strip=True)]
                    except: pass

            final_data = {
                "title": schema.get('title') or job_entry.get('title'),
                "company": company,
                "deadline": schema.get('validThrough') or get_visual_grid_data(soup, "Deadline"),
                "url": url,
                'responsibilities': responsibilities_list,
                "employment_status": schema.get('employmentType') or get_visual_grid_data(soup, "Employment Type"),
                "education": [grid_education] if grid_education != "Not found" else [],
                "experience": [grid_experience] if grid_experience != "Not found" else [],
                'additional_requirements': ["None specified"],
                "vacancy": grid_vacancy,
                "location": schema.get('jobLocation', {}).get('address', {}).get('addressLocality') or get_visual_grid_data(soup, "Location"),
                'age': 'Not specified',
                "salary": salary,
                "other_benefits": benefits_list,
                'published': published_raw,
                "skills": schema.get('skills', [])
            }

            all_job_data.append(final_data)
            logging.info(f" -> Scraped: {final_data['title']} | {final_data['salary']} | {final_data['company']}")

        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")

    driver.quit()

    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_job_data, f, indent=4, ensure_ascii=False)
    print(f"Done! Saved {len(all_job_data)} jobs to {OUTPUT_FILE}")





def scrape_details_memory(links):
    driver = setup_driver()
    all_job_data = []

    

    for i, job_entry in enumerate(links):
        url = job_entry.get('link') or job_entry.get('url')
        if not url: continue

        print(f"[{i+1}/{len(links)}] Processing: {url}")
        
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2) 

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            schema = extract_json_ld(soup)
            
            # --- Visual Grid Helpers ---
            grid_vacancy = get_visual_grid_data(soup, "Vacancy")
            grid_experience = get_visual_grid_data(soup, "Experience")
            grid_education = get_visual_grid_data(soup, "Education")
            
            # --- 1. Published Date (Todays Date) ---
            published_raw = datetime.now().strftime("%d %b %Y")

            # --- 2. Responsibilities Logic (Fixed) ---
            responsibilities_list = []
            
            # Try Schema first
            resp_html = schema.get('responsibilities', '') 
            if not resp_html: 
                resp_html = schema.get('description', '')
            
            if resp_html:
                responsibilities_list = clean_html_to_list(resp_html)
            
            # If still empty, try Visual Search for "Responsibilities" header
            if not responsibilities_list:
                try:
                    resp_header = soup.find(lambda tag: tag.name == "div" and "Responsibilities" in tag.get_text())
                    if resp_header:
                        # The content is usually in the next sibling div
                        content_div = resp_header.find_next_sibling("div")
                        if not content_div: # Sometimes it's inside a parent container structure
                            content_div = resp_header.parent.find_next_sibling("div")
                        if content_div:
                            responsibilities_list = clean_html_to_list(str(content_div))
                except: pass

            # --- 3. Company Logic (Fixed) ---
            company = schema.get('hiringOrganization', {}).get('name')
            # If schema misses it or gives generic name, use visual extraction
            if not company or company.lower() == "shomvob": 
                company = get_company_visual(soup)

            # --- 4. Salary Logic ---
            salary = "Negotiable"
            if schema.get('baseSalary'):
                try:
                    val = schema['baseSalary'].get('value', {})
                    min_s = val.get('minValue') or schema['baseSalary'].get('minValue')
                    max_s = val.get('maxValue') or schema['baseSalary'].get('maxValue')
                    if min_s:
                        salary = f"Tk. {min_s}" + (f" - {max_s}" if max_s else "") + " (Monthly)"
                except: pass
            
            if salary == "Negotiable":
                vis_sal = get_salary_visual(soup)
                if vis_sal: salary = vis_sal

            # --- Benefits ---
            benefits_list = schema.get('jobBenefits', [])
            if not benefits_list:
                ben_header = soup.find(string=re.compile("Benefits"))
                if ben_header:
                    try:
                        parent = ben_header.find_parent("div").find_parent("div")
                        benefits_list = [li.get_text(strip=True) for li in parent.find_all("div", class_="flex") if li.get_text(strip=True) and "Benefits" not in li.get_text(strip=True)]
                    except: pass

            final_data = {
                "title": schema.get('title') or job_entry.get('title'),
                "company": company,
                "deadline": schema.get('validThrough') or get_visual_grid_data(soup, "Deadline"),
                "url": url,
                'responsibilities': responsibilities_list,
                "employment_status": schema.get('employmentType') or get_visual_grid_data(soup, "Employment Type"),
                "education": [grid_education] if grid_education != "Not found" else [],
                "experience": [grid_experience] if grid_experience != "Not found" else [],
                'additional_requirements': ["None specified"],
                "vacancy": grid_vacancy,
                "location": schema.get('jobLocation', {}).get('address', {}).get('addressLocality') or get_visual_grid_data(soup, "Location"),
                'age': 'Not specified',
                "salary": salary,
                "other_benefits": benefits_list,
                'published': published_raw,
                "skills": schema.get('skills', [])
            }

            all_job_data.append(final_data)
            logging.info(f" -> Scraped: {final_data['title']} | {final_data['salary']} | {final_data['company']}")

        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")

    
    driver.quit()
    return all_job_data












if __name__ == "__main__":
    scrape_details()