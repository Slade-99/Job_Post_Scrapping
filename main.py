import time
import json
import random
import logging
import os
from datetime import datetime, timedelta
from BDJobs import bd_jobs_job_scrapper
from BDJobs import bd_jobs_link_scrapper
from Shomvob import somvob_filtering
from Shomvob import somvob_link_scrapper
from Shomvob import somvob_job_scrapper
import combined
from dotenv import load_dotenv
from pymongo import MongoClient

# --- CONFIGURATION ---
LOG_FILE = "service_log.txt"
START_HOUR = 1  # 1 AM
END_HOUR = 5    # 5 AM 

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("Error: MONGO_URI not found in .env file!")
else:
    print("Successfully loaded Mongo URI.")
DB_NAME = "test"
COLLECTION_NAME = "jobs"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
    force=True  
)

def get_mongo_collection():
    """Establishes connection and returns the collection."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

def get_existing_urls():
    """
    Fetches links from MongoDB to check for duplicates.
    """
    try:
        collection = get_mongo_collection()
        
        urls = set(collection.distinct("url"))
        
        
        links = set(collection.distinct("link"))
        
        
        all_known = urls.union(links)
        
        
        all_known.discard(None)
        
        logging.info(f"Database check: Found {len(all_known)} unique existing URLs.")
        return all_known
    except Exception as e:
        logging.error(f"Database Error: {e}")
        return set()

def save_to_database(new_jobs):
    """Inserts new jobs directly into MongoDB."""
    if not new_jobs:
        return

    try:
        collection = get_mongo_collection()
        collection.insert_many(new_jobs)
        logging.info(f"Successfully saved {len(new_jobs)} new jobs to MongoDB.")
    except Exception as e:
        logging.error(f"Failed to save to MongoDB: {e}")

def run_pipeline():
    logging.info("Starting Daily Scraping Pipeline...")
    
    
    existing_urls = get_existing_urls()
    
    # ==========================
    # STAGE 1: SHOMVOB
    # ==========================
    logging.info("--- Phase 1: Shomvob ---")
    
    
    all_shomvob_candidates = somvob_link_scrapper.scrape_shomvob_pagination(max_pages=6) 
    
    shomvob_links_to_process = []
    if not all_shomvob_candidates:
        logging.warning("No links found for Shomvob.")
    else:
        
        it_candidates = somvob_filtering.filter_it_jobs_memory(all_shomvob_candidates) 
        

        for job in it_candidates:
            current_link = job.get('link') or job.get('url')
            if current_link and current_link not in existing_urls:
                shomvob_links_to_process.append(job)

        logging.info(f"Shomvob: Found {len(it_candidates)} IT jobs. {len(shomvob_links_to_process)} are NEW.")


    shomvob_final_data = []
    if shomvob_links_to_process:
        shomvob_final_data = somvob_job_scrapper.scrape_details_memory(shomvob_links_to_process)

    # ==========================
    # STAGE 2: BDJOBS
    # ==========================
    logging.info("--- Phase 2: BDJobs ---")

    all_bdjobs_links = bd_jobs_link_scrapper.scrape_bdjobs() 

    bdjobs_final_data = [] 
    all_bdjobs_candidates = []
    
    if not all_bdjobs_links:
        logging.warning("No links found for BDJobs.")
    else:

        for job in all_bdjobs_links:
            current_link = job.get('link') or job.get('url')
            if current_link and current_link not in existing_urls:
                all_bdjobs_candidates.append(job)
                
        logging.info(f"BDJobs: Found {len(all_bdjobs_links)} total. {len(all_bdjobs_candidates)} are NEW.")

    if all_bdjobs_candidates:
        bdjobs_final_data = bd_jobs_job_scrapper.scrape_details_memory(all_bdjobs_candidates)

    # ==========================
    # STAGE 3: MERGE, CLEAN & CATEGORIZE
    # ==========================
    new_jobs_batch = shomvob_final_data + bdjobs_final_data
    
    if new_jobs_batch:
        final_clean_batch = []
        
        for job in new_jobs_batch:
            # 1. Categorize
            title = job.get('title', '')
            job['category'] = combined.assign_category(title)
            
            if 'link' in job:
                job['url'] = job['link']
                del job['link']
            
            if job.get('url'):
                final_clean_batch.append(job)

        save_to_database(final_clean_batch)
    else:
        logging.info("No new jobs found today.")

    logging.info("Daily Pipeline Completed.")

def get_seconds_until_next_run():
    """Calculates random time for tomorrow between START_HOUR and END_HOUR."""
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    
    random_hour = random.randint(START_HOUR, END_HOUR)
    random_minute = random.randint(0, 59)
    
    next_run = tomorrow.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    
    seconds_wait = (next_run - now).total_seconds()
    
    logging.info(f"--- Sleeping... Next run scheduled for: {next_run} ---")
    logging.info(f"--- Time to wait: {seconds_wait/3600:.2f} hours ---")
    
    return seconds_wait

if __name__ == "__main__":
    logging.info("Microservice Started.")

    logging.info("Executing immediate initial run...")
    try:
        run_pipeline()
    except Exception as e:
        logging.error(f"Critical Error in Initial Run: {e}")

    while True:
        wait_time = get_seconds_until_next_run()
        time.sleep(wait_time)
        
        try:
            run_pipeline()
        except Exception as e:
            logging.error(f"Critical Error in Pipeline: {e}")