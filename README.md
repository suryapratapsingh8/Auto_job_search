# 🧠 Automated Resume Parser (Week 1 of Job Automation Bot)

This module is the **Week 1 milestone** of the "Automated Resume & Job Application Bot" project.  
It parses a resume (PDF or DOCX), extracts key details like **name, email, phone, education, and skills**, and saves the structured output as JSON or in a database.

---

## 📁 Project Structure

Auto_job_search/
│── data/
│ └── resume.pdf # your input resume
│── modules/
│ └── resume_parser.py # core parser logic
│── output/
│ └── parsed_resume.json # structured output
│── main.py # runner script
│── requirements.txt
│── README.md