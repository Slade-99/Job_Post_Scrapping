# IT Job Scraper Microservice

## 1. Project Overview
This project is an automated microservice designed to scrape, filter, and categorize IT job postings from two major platforms: **Shomvob** and **BDJobs**.

The service runs continuously:
- Performs a full scraping pipeline immediately on startup.  
- Schedules the next run for a randomized time between **01:00 AM–05:00 AM** the following day, mimicking human behavior to avoid detection.

### **Key Features**
- **Multi-Source Scraping** — Scrapes job listings from Shomvob (via Selenium) and BDJobs (via Requests/Selenium).  
- **Smart Filtering** — Uses fuzzy matching and keyword scoring to detect IT jobs.  
- **Duplicate Detection** — Prevents reprocessing old job posts via `jobs.json`.  
- **Automatic Categorization** — Assigns jobs to predefined categories (Software, DevOps, Data/AI, etc.).  
- **Stealth Mode** — Randomized delays and rotating User-Agents reduce IP blocking.

---

## 2. Project Directory Structure  
Your files **must** follow this structure for imports in `main.py` to work:

```
root_directory/
│
├── main.py                     # Entry point (microservice orchestrator)
├── combined.py                 # Job categorization logic
├── requirements.txt            # Dependencies
├── jobs.json                   # Auto-generated job database
├── service_log.txt             # Auto-generated logs
│
├── BDJobs/
│   ├── __init__.py
│   ├── bd_jobs_link_scrapper.py
│   └── bd_jobs_job_scrapper.py
│
└── Shomvob/
    ├── __init__.py
    ├── somvob_link_scrapper.py
    ├── somvob_filtering.py
    └── somvob_job_scrapper.py
```

---

## 3. Prerequisites & Installation

### **A. System Requirements**
- Python 3.8+
- Google Chrome (latest version)
- Stable internet connection

### **B. Python Dependencies**
`requirements.txt` includes:

```
selenium
beautifulsoup4
requests
webdriver-manager
rapidfuzz
thefuzz
```

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## 4. Configuration

In `main.py`, you may adjust core settings:

```python
DATABASE_FILE = "jobs.json"  # Output DB file
START_HOUR = 1               # Earliest next-run hour (24h)
END_HOUR = 5                 # Latest next-run hour (24h)
```

Modify scraping depth:

```python
# Scrape more or fewer pages from Shomvob
all_shomvob_candidates = somvob_link_scrapper.scrape_shomvob_pagination(max_pages=6)
```

---

## 5. Module Details

### **main.py — Orchestrator**
**Responsibilities:**
1. Load existing jobs from `jobs.json`.  
2. **Phase 1 (Shomvob)**  
   - Scrape job links  
   - Filter by IT keywords  
   - Remove duplicates  
   - Scrape job details  

3. **Phase 2 (BDJobs)**  
   - Scrape list pages  
   - Remove duplicates  
   - Scrape job details  

4. **Phase 3 — Merge & Categorize**  
   - Combine results  
   - Categorize jobs using `combined.py`  
   - Save to database  

5. **Scheduling**  
   - Compute next run time (random between 1–5 AM)  
   - Sleep until next run  

---

### **Shomvob/ Modules**

#### `somvov_link_scrapper.py`
- Uses Selenium  
- Handles pagination, "Next" button detection  
- Collects job URLs  

#### `somvob_filtering.py`
- Uses **rapidfuzz**  
- Scores titles/descriptions against IT keyword list  
- Filters out irrelevant jobs (e.g., Sales, Driver, HR)

#### `somvob_job_scrapper.py`
- Scrapes job details  
- Attempts JSON-LD first  
- Falls back to HTML parsing (salary, responsibilities, etc.)

---

### **BDJobs/ Modules**

#### `bd_jobs_link_scrapper.py`
- Uses Requests + BeautifulSoup  
- Efficiently gathers job links from search results  

#### `bd_jobs_job_scrapper.py`
- Uses Selenium  
- Extracts education, experience, responsibilities via XPath  

---

### **combined.py — Categorization Logic**
- Assigns job categories (DevOps, Software Engineering, Data/AI, etc.)  
- Uses **thefuzz** to fuzzy match titles with predefined keyword lists.  

---

## 6. How to Run

1. Open a terminal.  
2. Navigate to the project root directory.  
3. Run:

```bash
python3 main.py
```

### **During Execution:**
- Chrome windows may open (unless running headless).  
- Logs appear in console and in `service_log.txt`.  
- When finished, you’ll see:

```
--- Sleeping... Next run scheduled for: [DATE TIME] ---
```

👉 **Do not close the terminal** if you want the system to run again the next day.

---

## 7. Troubleshooting

| Issue | Solution |
|-------|----------|
| **FileNotFoundError** | Check file paths. Ensure directory structure matches the README. |
| **ModuleNotFoundError** | Ensure `__init__.py` exists and all packages are installed. |
| **Chrome Driver Error** | Run `pip install --upgrade webdriver-manager` and ensure Chrome is installed. |
| **Script Hangs** | Selenium may be waiting for missing elements. Press `Ctrl + C` to restart. |