import json, re
from rapidfuzz import fuzz, process
from collections import Counter

# -------- CONFIG --------
INPUT_JSON = "BRAC_Project/Job_Post_Scrapping/Shomvob/links.json"
OUT_IT = "BRAC_Project/Job_Post_Scrapping/Shomvob/filtered.json"
OUT_NOT = "non_it.json"

# seed keywords for IT 
IT_KEYWORDS = [
    "software", "developer", "programmer", "backend", "frontend",
    "fullstack", "devops", "data scientist", "data scientist", "machine learning",
    "ML", "AI", "artificial intelligence", "cloud", "aws", "azure", "gcp",
    "django", "flask", "react", "vue", "angular", "java", "python", "c++", "c#",
    "node", "javascript", "php", "sql", "database", "android", "ios", "mobile",
    "QA", "tester", "automation", "site reliability", "sre","Video","Page","Content","Digital","3D","Customer","Social Media",
    "Dev", " Data Analyst "," IT Support"," IT Specialist"," IT Consultant"," Network Engineer"," System Administrator",
    " Cybersecurity"," Security Analyst"," Cloud Engineer"," Software Architect"," Web Developer"," Mobile Developer"," Database Administrator",
    " Machine Learning Engineer"," AI Specialist"," Data Engineer"," Frontend Developer"," Backend Developer",
    "Full Stack Developer"," DevOps Engineer"," QA Engineer"," Test Automation Engineer"," Site Reliability Engineer"," IT Director",
    " Information Technology"," Information Systems"," Computer Science"," Computer Engineering","Computer Operator"," Computer Technician"," Computer Programmer"," Software Development"," Software Engineering",
    " Web Design"," Web Development"," Network Administration"," System Administration"," Cybersecurity Analyst"," Data Science"," Data Analytics"," Business Intelligence"," Cloud Computing"," Cloud Services"," Cloud Solutions"," Cloud Infrastructure",
    "Page Moderator","Content Creator","Digital Marketing","Digital Content","Social Media Specialist","Social Media Coordinator",
    "Customer Support","Computer Operator","Computer Technician","Customer Service","Customer Success","Customer Experience","Customer Relations","Call Center Agent","Technical Support","Help Desk","IT Helpdesk","IT Support Specialist","IT Support Technician",
    "Digital Marketing","Digital Content","Social Media Manager","Social Media Specialist","Social Media Coordinator",
    "Laravel Developer","React Developer","Angular Developer","Vue Developer","Node.js Developer","Python Developer","Java Developer","C# Developer","C++ Developer",
    "Graphics Designer","UI/UX Designer","Product Designer","Visual Designer","Motion Graphics","3D Artist","Animator","Video Editor","Multimedia Specialist",
    "Video Editor","Full stack developer","Web developer","Software developer","Mobile app developer","Game developer","Database administrator",
    "Network administrator","System administrator","IT support specialist","Cybersecurity analyst","Cloud solutions architect","Graphics Designer",
    "Customer Service","Digital Strategist","SEO Specialist","Email Marketing Specialist",
    "Social Media Strategist","Scrum Master","Agile Coach","Business Analyst","Data Analyst","Data Scientist","Machine Learning Engineer","AI Researcher","DevOps Engineer","Site Reliability Engineer","IT Director","ISP","Computer Hardware Repair",
    "Technical Writer","IT Auditor","IT Trainer","Help Desk Technician","Network Security Specialist","Systems Analyst","Cloud Administrator","Cloud Security Specialist","Big Data Engineer",
    'CCTV Installation',' Office Networking','Support Engineer,'
]

# thresholds
KEYWORD_MATCH_MIN = 1         # at least 1 exact keyword hit
FUZZY_SCORE_THRESHOLD = 80      # fuzzy match threshold (0-100)
COMBINED_SCORE_THRESHOLD = 0.21  # final combined score threshold (0-1)


def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def keyword_hits(text, keywords):
    text_n = normalize(text)
    hits = [kw for kw in keywords if kw in text_n]
    return hits

def fuzzy_best_score(text, keywords):
    text_n = normalize(text)
    best = 0
    best_kw = None
    for kw in keywords:
        s = fuzz.token_set_ratio(kw, text_n)  # 0-100
        if s > best:
            best = s
            best_kw = kw
    return best, best_kw


def filter_it_jobs_memory(jobs):
    it_list = []
    non_it_list = []

    for j in jobs:
        title = j.get("title", "") or ""
        desc = j.get("description", "") or ""   
        text = " ".join([title, desc])

        hits = keyword_hits(text, IT_KEYWORDS)
        fuzzy_score, fuzzy_kw = fuzzy_best_score(text, IT_KEYWORDS)

        # combine heuristic: prefer exact keyword hits but also accept fuzzy high score
        score = 0.0
        if len(hits) >= KEYWORD_MATCH_MIN:
            score += 0.7 
        
        score += (fuzzy_score / 100.0) * 0.3

        j["_heuristic"] = {
            "keyword_hits": hits,
            "fuzzy_score": fuzzy_score,
            "fuzzy_kw": fuzzy_kw,
            "combined_score": round(score, 3)
        }

        if score >= COMBINED_SCORE_THRESHOLD:
            it_list.append(j)
        else:
            non_it_list.append(j)
        
        return it_list