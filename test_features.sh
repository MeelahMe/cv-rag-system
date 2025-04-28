#!/bin/bash

echo "📝 Inserting a CV..."
curl -X POST http://localhost:8000/insert/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe is a senior data scientist with 5 years of experience in machine learning and Python.",
    "language": "English",
    "skills": ["Python", "Machine Learning"],
    "job_title": "Senior Data Scientist",
    "years_experience": 5
}'
echo ""
echo " Insert Done"
echo ""

echo "🔍 Basic Search..."
curl -X POST http://localhost:8000/search/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "top_k": 5
}'
echo ""
echo " Basic Search Done"
echo ""

echo "🎯 Filtered Search..."
curl -X POST http://localhost:8000/search/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "data scientist",
    "top_k": 5,
    "language": "English",
    "min_years_experience": 3,
    "skills": ["Python"],
    "job_title": "Senior Data Scientist"
}'
echo ""
echo " Filtered Search Done"
echo ""

echo "📈 Scoring Query against CV..."
curl -X POST http://localhost:8000/score/score \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning expert",
    "text": "John Doe is a senior data scientist with 5 years of experience in machine learning and Python."
}'
echo ""
echo " Scoring Done"
echo ""

echo "🏁 All tests finished."

