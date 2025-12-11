import json
from thefuzz import process, fuzz

CATEGORY_MAPPING = {
    "Software Engineering": [
        'software developer',"software engineer","developer", "programmer", "backend", "frontend",
        "fullstack", "django", "flask", "react", "vue", "angular", "java", "python", 
        "c++", "c#", "node", "javascript", "php", "sql", "android", "ios", "mobile", 
        "web developer", "mobile app developer", "game developer", "laravel"
    ],
    "Data & AI": [
        "data scientist", "machine learning", "ML", "AI", "artificial intelligence", 
        "data analyst", "data engineer", "big data", "business intelligence", 
        "data analytics", "ai researcher"
    ],
    "DevOps & Cloud": [
        "devops", "cloud", "aws", "azure", "gcp", "site reliability", "sre", 
         "sysadmin", "system administrator", "cloud engineer", 
        "cloud architect", "network administrator", "server"
    ],
    "IT Support & Hardware": [
        "it support", "help desk", "technician", "computer operator", "hardware", 
        "network", "cctv", "repair", "isp", "technical support", "computer technician"
    ],
    "Cybersecurity": [
        "cybersecurity", "security analyst", "security engineer", "infosec", 
        "auditor", "network security", "security specialist"
    ],
    "Design & Creative": [
        "graphics", "ui/ux", "product designer", "visual designer", "motion", 
        "3d", "animator", "video editor", "multimedia", "adobe", "photoshop"
    ],
    "Marketing & Content": [
        "digital marketing", "seo", "social media", "content creator", "content manager", 
        "marketing specialist", "ppc", "brand manager", "community manager", "affiliate"
    ],
    "Management & Product": [
        "project manager", "product manager", "scrum master", "agile", "business analyst", 
        "it manager", "it director", "customer success", "customer support", "customer service"
    ],
    "QA & Testing": [
        "qa", "tester", "automation", "quality assurance", "test engineer"
    ]
}

def assign_category(job_title):
    """
    Matches the job title against all keyword lists using fuzzy logic.
    Returns the category name with the highest matching score.
    """
    best_category = "Uncategorized"
    highest_score = 0
    
   
    clean_title = str(job_title).lower()

    for category, keywords in CATEGORY_MAPPING.items():

        match = process.extractOne(clean_title, keywords, scorer=fuzz.token_set_ratio)
        
        if match:
            score = match[1]
            
            if score > highest_score:
                highest_score = score
                best_category = category

    # Threshold: Only assign if we are at least 60% sure
    if highest_score < 60:
        return "Other / Uncategorized"
        
    return best_category

def run_pipeline():
    
    try:
        with open('BRAC_Project/Job_Post_Scrapping/BDJobs/job_details.json', 'r', encoding='utf-8') as f1:
            data1 = json.load(f1)
        with open('BRAC_Project/Job_Post_Scrapping/Shomvob/shomvob_job_details.json', 'r', encoding='utf-8') as f2:
            data2 = json.load(f2)
    except FileNotFoundError:
        print("Error: Could not find file1.json or file2.json")
        return

    
    combined_jobs = data1 + data2
    print(f"Processing {len(combined_jobs)} jobs...")

    
    processed_data = []
    
    for job in combined_jobs:

        title = job.get('title', '') or job.get('job_title', '') 
        
        category = assign_category(title)
        
        job['category'] = category
        processed_data.append(job)
        

    with open('BRAC_Project/Job_Post_Scrapping/jobs.json', 'w', encoding='utf-8') as out_file:
        json.dump(processed_data, out_file, indent=2, ensure_ascii=False)

    print("Success! Saved to 'jobs.json'")

