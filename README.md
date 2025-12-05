# IT Job Scraper Microservice

## 1. Project Overview
This project is an automated microservice designed to scrape, filter, and categorize IT job postings from two major platforms: **Shomvob** and **BDJobs**.

The service runs continuously. It executes a full scraping pipeline immediately upon startup, and then schedules subsequent runs for the next day at a randomized time (between 01:00 AM and 05:00 AM) to mimic human behavior and avoid detection.

**Key Features:**
* **Multi-Source Scraping:** Fetches jobs from Shomvob (via Selenium) and BDJobs (via Requests/Selenium).
* **Smart Filtering:** Uses fuzzy logic and keyword matching to filter out non-IT jobs from general listings.
* **Duplicate Detection:** Checks against a local database (`jobs.json`) to ensure only new jobs are processed.
* **Automatic Categorization:** Classifies jobs into categories like "Software Engineering", "DevOps", "Data & AI", etc.
* **Stealth Mode:** Uses randomized sleep intervals and User-Agents to prevent IP blocking.

---

## 2. Project Directory Structure
**Critical:** For the imports in `main.py` to work, your files must be organized exactly as shown below:

```text
root_directory/
│
├── main.py                    # Entry point (The Microservice)
├── combined.py                # Categorization logic
├── requirements.txt           # Python dependencies
├── jobs.json                  # The main database (Auto-generated)
├── service_log.txt            # Execution logs (Auto-generated)
│
├── BDJobs/                    # Package for BDJobs scripts
│   ├── __init__.py            # (Create empty file)
│   ├── bd_jobs_link_scrapper.py
│   └── bd_jobs_job_scrapper.py
│
└── Shomvob/                   # Package for Shomvob scripts
    ├── __init__.py            # (Create empty file)
    ├── somvob_link_scrapper.py
    ├── somvob_filtering.py
    └── somvob_job_scrapper.py



##  3. Prerequisites & Installation
A. System Requirements
Python 3.8+

Google Chrome Browser (Latest version)

Stable Internet Connection

B. Python Dependencies
Create a file named requirements.txt and paste the following:
selenium
beautifulsoup4
requests
webdriver-manager
rapidfuzz
thefuzz

Install them using pip:
pip install -r requirements.txt


I cannot directly generate a downloadable file (like a .md attachment), but I can provide the raw Markdown code below.

How to use this:

Create a new file in your project folder named README.md.

Click the "Copy" button on the code block below.

Paste the content into your new file and save it.

Markdown

# IT Job Scraper & Aggregator Microservice

## 1. Project Overview
This project is an automated microservice designed to scrape, filter, and categorize IT job postings from two major platforms: **Shomvob** and **BDJobs**.

The service runs continuously. It executes a full scraping pipeline immediately upon startup, and then schedules subsequent runs for the next day at a randomized time (between 01:00 AM and 05:00 AM) to mimic human behavior and avoid detection.

**Key Features:**
* **Multi-Source Scraping:** Fetches jobs from Shomvob (via Selenium) and BDJobs (via Requests/Selenium).
* **Smart Filtering:** Uses fuzzy logic and keyword matching to filter out non-IT jobs from general listings.
* **Duplicate Detection:** Checks against a local database (`jobs.json`) to ensure only new jobs are processed.
* **Automatic Categorization:** Classifies jobs into categories like "Software Engineering", "DevOps", "Data & AI", etc.
* **Stealth Mode:** Uses randomized sleep intervals and User-Agents to prevent IP blocking.

---

## 2. Project Directory Structure
**Critical:** For the imports in `main.py` to work, your files must be organized exactly as shown below:

```text
root_directory/
│
├── main.py                    # Entry point (The Microservice)
├── combined.py                # Categorization logic
├── requirements.txt           # Python dependencies
├── jobs.json                  # The main database (Auto-generated)
├── service_log.txt            # Execution logs (Auto-generated)
│
├── BDJobs/                    # Package for BDJobs scripts
│   ├── __init__.py            # (Create empty file)
│   ├── bd_jobs_link_scrapper.py
│   └── bd_jobs_job_scrapper.py
│
└── Shomvob/                   # Package for Shomvob scripts
    ├── __init__.py            # (Create empty file)
    ├── somvob_link_scrapper.py
    ├── somvob_filtering.py
    └── somvob_job_scrapper.py
Note: The scripts currently reference a path BRAC_Project/Job_Post_Scrapping/. You should either create these folders or update the INPUT_FILE / OUTPUT_FILE paths in the scripts to match your local setup.

3. Prerequisites & Installation
A. System Requirements
Python 3.8+

Google Chrome Browser (Latest version)

Stable Internet Connection

B. Python Dependencies
Create a file named requirements.txt and paste the following:

Plaintext

selenium
beautifulsoup4
requests
webdriver-manager
rapidfuzz
thefuzz
Install them using pip:

Bash

pip install -r requirements.txt


4. Configuration
You can adjust the behavior of the microservice by modifying the constants at the top of main.py


# main.py

DATABASE_FILE = "jobs.json"  # Output file for all jobs
START_HOUR = 1               # Earliest start time for next day run (24h format)
END_HOUR = 5                 # Latest start time for next day run (24h format)

I cannot directly generate a downloadable file (like a .md attachment), but I can provide the raw Markdown code below.

How to use this:

Create a new file in your project folder named README.md.

Click the "Copy" button on the code block below.

Paste the content into your new file and save it.

Markdown

# IT Job Scraper & Aggregator Microservice

## 1. Project Overview
This project is an automated microservice designed to scrape, filter, and categorize IT job postings from two major platforms: **Shomvob** and **BDJobs**.

The service runs continuously. It executes a full scraping pipeline immediately upon startup, and then schedules subsequent runs for the next day at a randomized time (between 01:00 AM and 05:00 AM) to mimic human behavior and avoid detection.

**Key Features:**
* **Multi-Source Scraping:** Fetches jobs from Shomvob (via Selenium) and BDJobs (via Requests/Selenium).
* **Smart Filtering:** Uses fuzzy logic and keyword matching to filter out non-IT jobs from general listings.
* **Duplicate Detection:** Checks against a local database (`jobs.json`) to ensure only new jobs are processed.
* **Automatic Categorization:** Classifies jobs into categories like "Software Engineering", "DevOps", "Data & AI", etc.
* **Stealth Mode:** Uses randomized sleep intervals and User-Agents to prevent IP blocking.

---

## 2. Project Directory Structure
**Critical:** For the imports in `main.py` to work, your files must be organized exactly as shown below:

```text
root_directory/
│
├── main.py                    # Entry point (The Microservice)
├── combined.py                # Categorization logic
├── requirements.txt           # Python dependencies
├── jobs.json                  # The main database (Auto-generated)
├── service_log.txt            # Execution logs (Auto-generated)
│
├── BDJobs/                    # Package for BDJobs scripts
│   ├── __init__.py            # (Create empty file)
│   ├── bd_jobs_link_scrapper.py
│   └── bd_jobs_job_scrapper.py
│
└── Shomvob/                   # Package for Shomvob scripts
    ├── __init__.py            # (Create empty file)
    ├── somvob_link_scrapper.py
    ├── somvob_filtering.py
    └── somvob_job_scrapper.py
Note: The scripts currently reference a path BRAC_Project/Job_Post_Scrapping/. You should either create these folders or update the INPUT_FILE / OUTPUT_FILE paths in the scripts to match your local setup.

3. Prerequisites & Installation
A. System Requirements
Python 3.8+

Google Chrome Browser (Latest version)

Stable Internet Connection

B. Python Dependencies
Create a file named requirements.txt and paste the following:

Plaintext

selenium
beautifulsoup4
requests
webdriver-manager
rapidfuzz
thefuzz
Install them using pip:

Bash

pip install -r requirements.txt
4. Configuration
You can adjust the behavior of the microservice by modifying the constants at the top of main.py:

Python

# main.py

DATABASE_FILE = "jobs.json"  # Output file for all jobs
START_HOUR = 1               # Earliest start time for next day run (24h format)
END_HOUR = 5                 # Latest start time for next day run (24h format)


You can also adjust the scraping depth (number of pages) inside run_pipeline in main.py
# Adjust max_pages to scrape more or fewer pages from Shomvob
all_shomvob_candidates = somvob_link_scrapper.scrape_shomvob_pagination(max_pages=22)



I cannot directly generate a downloadable file (like a .md attachment), but I can provide the raw Markdown code below.

How to use this:

Create a new file in your project folder named README.md.

Click the "Copy" button on the code block below.

Paste the content into your new file and save it.

Markdown

# IT Job Scraper & Aggregator Microservice

## 1. Project Overview
This project is an automated microservice designed to scrape, filter, and categorize IT job postings from two major platforms: **Shomvob** and **BDJobs**.

The service runs continuously. It executes a full scraping pipeline immediately upon startup, and then schedules subsequent runs for the next day at a randomized time (between 01:00 AM and 05:00 AM) to mimic human behavior and avoid detection.

**Key Features:**
* **Multi-Source Scraping:** Fetches jobs from Shomvob (via Selenium) and BDJobs (via Requests/Selenium).
* **Smart Filtering:** Uses fuzzy logic and keyword matching to filter out non-IT jobs from general listings.
* **Duplicate Detection:** Checks against a local database (`jobs.json`) to ensure only new jobs are processed.
* **Automatic Categorization:** Classifies jobs into categories like "Software Engineering", "DevOps", "Data & AI", etc.
* **Stealth Mode:** Uses randomized sleep intervals and User-Agents to prevent IP blocking.

---

## 2. Project Directory Structure
**Critical:** For the imports in `main.py` to work, your files must be organized exactly as shown below:

```text
root_directory/
│
├── main.py                    # Entry point (The Microservice)
├── combined.py                # Categorization logic
├── requirements.txt           # Python dependencies
├── jobs.json                  # The main database (Auto-generated)
├── service_log.txt            # Execution logs (Auto-generated)
│
├── BDJobs/                    # Package for BDJobs scripts
│   ├── __init__.py            # (Create empty file)
│   ├── bd_jobs_link_scrapper.py
│   └── bd_jobs_job_scrapper.py
│
└── Shomvob/                   # Package for Shomvob scripts
    ├── __init__.py            # (Create empty file)
    ├── somvob_link_scrapper.py
    ├── somvob_filtering.py
    └── somvob_job_scrapper.py
Note: The scripts currently reference a path BRAC_Project/Job_Post_Scrapping/. You should either create these folders or update the INPUT_FILE / OUTPUT_FILE paths in the scripts to match your local setup.

3. Prerequisites & Installation
A. System Requirements
Python 3.8+

Google Chrome Browser (Latest version)

Stable Internet Connection

B. Python Dependencies
requirements.txt has the following:

selenium
beautifulsoup4
requests
webdriver-manager
rapidfuzz
thefuzz
Install them using pip:

Bash

pip install -r requirements.txt
4. Configuration
You can adjust the behavior of the microservice by modifying the constants at the top of main.py:

Python

# main.py

DATABASE_FILE = "jobs.json"  # Output file for all jobs
START_HOUR = 1               # Earliest start time for next day run (24h format)
END_HOUR = 5                 # Latest start time for next day run (24h format)
You can also adjust the scraping depth (number of pages) inside run_pipeline in main.py:

Python

# Adjust max_pages to scrape more or fewer pages from Shomvob
all_shomvob_candidates = somvob_link_scrapper.scrape_shomvob_pagination(max_pages=22)




5. Module Details
main.py (The Orchestrator)
Role: Controls the entire workflow.

Workflow:

Loads existing jobs from jobs.json.

Phase 1 (Shomvob): Scrapes all links -> Filters for IT keywords -> Removes duplicates -> Scrapes detailed descriptions.

Phase 2 (BDJobs): Scrapes search pages -> Removes duplicates -> Scrapes detailed descriptions.

Phase 3 (Merge): Combines data, assigns categories via combined.py, and saves to the database.

Scheduling: Calculates a random time for the next day and sleeps until then.

Shomvob/ Modules
somvob_link_scrapper.py: Uses Selenium to iterate through pagination on Shomvob. Handles the "Next" button logic and extracts job links.

somvob_filtering.py: Uses rapidfuzz to score job titles/descriptions against a list of IT keywords. Filters out non-relevant jobs (e.g., "Driver", "Sales").

somvob_job_scrapper.py: Visits individual job links. Tries to extract data from Schema.org JSON-LD (hidden metadata). If that fails, it falls back to visual HTML parsing (finding "Salary", "Responsibilities" visually).

BDJobs/ Modules
bd_jobs_link_scrapper.py: Uses requests and BeautifulSoup to quickly grab job links from search result pages.

bd_jobs_job_scrapper.py: Uses Selenium to visit specific job pages. It uses specific XPaths to extract "Experience", "Education", and "Responsibilities".

combined.py (Categorization)
Role: Takes the final merged list of jobs and assigns a category (e.g., "DevOps & Cloud", "Software Engineering") based on the job title.

Logic: Uses thefuzz library to fuzzy match job titles against predefined keyword lists.



6. How to Run

1.Open your terminal or command prompt.

2.Navigate to the project root directory.

3.Run the main script:


What to expect:

The script will start immediately.

Chrome windows will open and close (unless running in Headless mode).

Logs will appear in the console and service_log.txt.

Once finished, it will display: --- Sleeping... Next run scheduled for: [Date Time] ---.

Do not close the terminal if you want it to run automatically the next day.





7. Troubleshooting
Issue,Solution
FileNotFoundError,Check the file paths in the scripts. Ensure BRAC_Project/Job_Post_Scrapping/... folders exist or rename paths in code to ./.
ModuleNotFoundError,Ensure you have the __init__.py files in the subfolders and have run pip install.
Chrome Driver Error,Run pip install --upgrade webdriver-manager. Ensure you have Chrome installed.
Script hangs,"Occasionally Selenium waits for elements that don't load. The script has timeouts, but you may need to force quit (Ctrl+C) and restart."