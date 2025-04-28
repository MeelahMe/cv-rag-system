#!/bin/bash

echo "Inserting sample CVs..."

curl -X POST http://localhost:8000/insert-cv \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe is a senior data scientist with 5 years of experience in machine learning and Python.",
    "language": "English",
    "skills": ["Python", "Machine Learning"],
    "job_title": "Senior Data Scientist",
    "years_experience": 5
}'
echo ""

curl -X POST http://localhost:8000/insert-cv \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Jane Smith is a junior software developer with 1 year of experience in JavaScript and React.",
    "language": "English",
    "skills": ["JavaScript", "React"],
    "job_title": "Software Developer",
    "years_experience": 1
}'
echo ""

curl -X POST http://localhost:8000/insert-cv \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Carlos Ruiz is a senior backend engineer with 8 years of experience in Go and Kubernetes.",
    "language": "Spanish",
    "skills": ["Go", "Kubernetes"],
    "job_title": "Backend Engineer",
    "years_experience": 8
}'
echo ""

curl -X POST http://localhost:8000/insert-cv \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Aisha Khan is a data analyst with 3 years of experience in SQL and Tableau.",
    "language": "English",
    "skills": ["SQL", "Tableau"],
    "job_title": "Data Analyst",
    "years_experience": 3
}'
echo ""

curl -X POST http://localhost:8000/insert-cv \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mohammed Al-Fulan is a machine learning engineer with 6 years of experience in Python and TensorFlow.",
    "language": "Arabic",
    "skills": ["Python", "TensorFlow"],
    "job_title": "Machine Learning Engineer",
    "years_experience": 6
}'
echo ""

echo "Bulk insert completed."
