import time
import json
import random
import logging
import os
from datetime import datetime, timedelta

# --- IMPORT YOUR EXISTING MODULES ---
# Ensure these files are in the same directory or properly referenced
# You might need to slightly refactor your scripts to expose these functions
from BDJobs import bd_jobs_job_scrapper
from BDJobs import bd_jobs_link_scrapper
from Shomvob import somvob_filtering
from Shomvob import somvob_link_scrapper
from Shomvob import somvob_job_scrapper
import combined

# --- CONFIGURATION ---
DATABASE_FILE = "jobs.json" # This holds ALL historical data
LOG_FILE = "service_log.txt"
START_HOUR = 1  # 1 AM
END_HOUR = 5    # 5 AM 

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def load_database():
    """Loads the existing database to check for duplicates."""
    if not os.path.exists(DATABASE_FILE):
        return []
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_to_database(new_jobs):
    current_db = load_database()
    updated_db = current_db + new_jobs
    
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_db, f, indent=4, ensure_ascii=False)
    logging.info(f"Successfully saved {len(new_jobs)} new jobs to database.")

def get_existing_urls(database):
    """Creates a set of URLs already in the DB for fast lookup."""
    return {job.get('url') or job.get('link') for job in database}

def run_pipeline():
    logging.info("Starting Daily Scraping Pipeline...")
    
    # 1. Load History (To avoid redundancy)
    existing_urls = get_existing_urls(load_database())
    logging.info(f"Loaded {len(existing_urls)} existing jobs from database.")

    # ==========================
    # STAGE 1: SHOMVOB
    # ==========================
    logging.info("--- Phase 1: Shomvob ---")
    
    all_shomvob_candidates = somvob_link_scrapper.scrape_shomvob_pagination(max_pages=22) 
    
    if not all_shomvob_candidates:
        logging.warning("No links found for Shomvob.")
        shomvob_links_to_process = []
    else:
        it_candidates = somvob_filtering.filter_it_jobs_memory(all_shomvob_candidates) 
        
       
        shomvob_links_to_process = [
            job for job in it_candidates 
            if job.get('link') not in existing_urls
        ]
        logging.info(f"Shomvob: Found {len(it_candidates)} IT jobs. {len(shomvob_links_to_process)} are NEW.")

    # D. Scrape Details for NEW links only
    shomvob_final_data = []
    if shomvob_links_to_process:
        
        shomvob_final_data = somvob_job_scrapper.scrape_details_memory(shomvob_links_to_process)



    # ==========================
    # STAGE 2: BDJOBS (Placeholder)
    # ==========================
    logging.info("--- Phase 2: BDJobs ---")

    all_bdjobs_links = bd_jobs_link_scrapper.scrape_bdjobs() 

    bdjobs_final_data = [] 
    if not all_bdjobs_links:
        logging.warning("No links found for Shomvob.")
        all_bdjobs_candidates = []
    else:
        all_bdjobs_candidates = [
            job for job in all_bdjobs_links 
            if job.get('link') not in existing_urls
        ]
        logging.info(f"BDJobs: Found {len(it_candidates)} IT jobs. {len(shomvob_links_to_process)} are NEW.")

    
    
    if all_bdjobs_candidates:
        
        bdjobs_final_data = bd_jobs_job_scrapper.scrape_details_memory(all_bdjobs_candidates)
    # ==========================
    # STAGE 3: MERGE & CATEGORIZE
    # ==========================
    new_jobs_batch = shomvob_final_data + bdjobs_final_data
    
    if new_jobs_batch:
        # Apply your combined.py categorization
        for job in new_jobs_batch:
            title = job.get('title', '')
            job['category'] = combined.assign_category(title)

        
        save_to_database(new_jobs_batch)
    else:
        logging.info("No new jobs found today.")

    logging.info("Daily Pipeline Completed.")

def get_seconds_until_next_run():
    """Calculates random time for tomorrow between START_HOUR and END_HOUR."""
    now = datetime.now()
    # Always schedule for the next calendar day
    tomorrow = now + timedelta(days=1)
    
    # Set random time window for tomorrow
    random_hour = random.randint(START_HOUR, END_HOUR)
    random_minute = random.randint(0, 59)
    
    next_run = tomorrow.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    
    seconds_wait = (next_run - now).total_seconds()
    
    logging.info(f"--- Sleeping... Next run scheduled for: {next_run} ---")
    logging.info(f"--- Time to wait: {seconds_wait/3600:.2f} hours ---")
    
    return seconds_wait

if __name__ == "__main__":
    logging.info("Microservice Started.")

    # --- STEP 1: RUN IMMEDIATELY ---
    # This runs exactly once when you start the script
    logging.info("Executing immediate initial run...")
    try:
        run_pipeline()
    except Exception as e:
        logging.error(f"Critical Error in Initial Run: {e}")

    # --- STEP 2: LOOP FOREVER (NEXT DAY & SO ON) ---
    while True:
        # Calculate time until tomorrow's random slot
        wait_time = get_seconds_until_next_run()
        
        # Sleep until that time
        time.sleep(wait_time)
        
        # Wake up and run
        try:
            run_pipeline()
        except Exception as e:
            logging.error(f"Critical Error in Pipeline: {e}")
            # Loop continues even if there is an error