import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import random
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_bdjobs():

    base_url = "https://jobs.bdjobs.com/"
    all_jobs_data = []
    x = random.randint(2, 6)
    
    for page_num in range(1, x):
        # Construct the URL for the current page
        search_url = f"https://jobs.bdjobs.com/jobsearch.asp?txtsearch=&fcat=8&qOT=0&iCat=0&Country=0&qPosted=0&qDeadline=0&Newspaper=0&qJobNature=0&qJobLevel=0&qExp=0&qAge=0&hidOrder=&pg={page_num}&rpp=100&hidJobSearch=JobSearch&MPostings=&ver=&strFlid_fvalue=&strFilterName=&hClickLog=1&earlyAccess=0&fcatId=8&hPopUpVal=1"
        logging.info(f"--- Scraping page {page_num}: {search_url} ---")

        try:
            # Send a GET request to the URL. Using a timeout is a good practice.
            # Added headers to mimic a real browser visit.
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, timeout=15, headers=headers)
            
            # Raise an HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all job posting blocks. Bdjobs uses several similar class names for them.
            # This list includes 'norm-jobs-wrapper' to be more comprehensive.
            job_blocks = soup.find_all('div', class_=['norm-jobs-wrapper', 'norm-job-block', 'sout-job-block', 'job-block'])

            if not job_blocks:
                logging.warning(f"No job postings found on page {page_num}. This might be the last page.")
                break # Exit the loop if a page has no jobs

            logging.info(f"Found {len(job_blocks)} job postings on page {page_num}. Extracting details...")

            for job_card in job_blocks:
                job_info = {}

                # --- Extract Title and Link ---
                # The title and link are within a <a> tag inside a div with class 'job-title-text'
                title_element = job_card.find('div', class_='job-title-text')
                if title_element and title_element.find('a'):
                    link_tag = title_element.find('a')
                    # Get the text, stripping any extra whitespace
                    job_info['title'] = link_tag.get_text(strip=True)
                    # The href attribute contains a relative path, so we prepend the base URL
                    job_info['link'] = link_tag['href']
                else:
                    # Skip this card if a title/link can't be found
                    continue

                # --- Extract Deadline ---
                # The deadline can be in a div with class 'dead-text' or 'dead-line'
                deadline_element = job_card.find('div', class_='dead-text')
                if not deadline_element: # Fallback to the old class name if the new one isn't found
                    deadline_element = job_card.find('div', class_='dead-line')

                if deadline_element:
                    job_info['deadline'] = deadline_element.get_text(strip=True)
                else:
                    job_info['deadline'] = "Not specified"

                all_jobs_data.append(job_info)

            # Add a respectful delay of 2 seconds between requests
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching page {page_num}: {e}")
            continue # Skip to the next page if an error occurs
        except Exception as e:
            logging.error(f"An unexpected error occurred on page {page_num}: {e}")
            continue

    # --- Save all the collected data to a JSON file ---
    return all_jobs_data



if __name__ == '__main__':
    # This block ensures the function runs only when the script is executed directly
    scrape_bdjobs()


