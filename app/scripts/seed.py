# app/scripts/seed.py

import os
import requests
from faker import Faker
from random import randint, choice

# Load environment variables
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "your-super-secret-key-here")

fake = Faker()

# Define some skill pools
SKILLS = [
    "Python", "Machine Learning", "Data Analysis", "SQL", "JavaScript", "React",
    "Go", "Kubernetes", "AWS", "Docker", "TensorFlow", "Pandas", "Django"
]

JOB_TITLES = [
    "Data Scientist", "Software Engineer", "Backend Developer", "ML Engineer", "DevOps Engineer"
]

LANGUAGES = ["English", "Spanish", "Arabic"]

def generate_fake_cv():
    language = choice(LANGUAGES)
    
    if language == "Arabic":
        text = "أحمد العلي مهندس بيانات لديه خمس سنوات من الخبرة في التحليل والبرمجة بلغة بايثون."
        job_title = "مهندس بيانات"
        skills = ["Python", "Data Analysis", "Machine Learning"]
    elif language == "Spanish":
        text = "María González es una ingeniera de software con 4 años de experiencia en desarrollo backend utilizando Python y Django."
        job_title = "Ingeniera de Software"
        skills = ["Python", "Backend Development", "Django"]
    else:  # English
        text = f"{fake.name()} is a {choice(JOB_TITLES)} with {randint(1, 10)} years of experience specializing in {choice(SKILLS)}."
        job_title = choice(JOB_TITLES)
        skills = fake.words(nb=5, ext_word_list=SKILLS)
    
    return {
        "text": text,
        "language": language,
        "skills": skills,
        "job_title": job_title,
        "years_experience": randint(1, 10)
    }

def insert_cv(cv):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    response = requests.post(f"{API_URL}/insert-cv", json=cv, headers=headers)
    if response.status_code == 200:
        print(f"Inserted CV ({cv['language']}): {cv['text'][:30]}...")
    else:
        print(f"Failed to insert CV: {response.status_code} - {response.text}")

def main():
    num_cvs = 20  # You can adjust this number
    for _ in range(num_cvs):
        cv = generate_fake_cv()
        insert_cv(cv)

if __name__ == "__main__":
    main()
