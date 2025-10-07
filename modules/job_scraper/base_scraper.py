# modules/job_scraper/base_scraper.py
import os
import json
import sqlite3
from datetime import datetime

class BaseScraper:
    """Common logic for all job scrapers."""

    def __init__(self, source_name):
        self.source_name = source_name

    def save_to_json(self, jobs, output_path="data/scraped_jobs.json"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=4)
        print(f"✅ Saved {len(jobs)} jobs from {self.source_name} to {output_path}")

    def save_to_db(self, jobs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "..", "..", "data", "resume.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                company TEXT,
                skills TEXT,
                location TEXT,
                source TEXT,
                scraped_at TEXT
            )
        """)

        for job in jobs:
            cur.execute("""
                INSERT INTO jobs (title, company, skills, location, source, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                job.get("title"),
                job.get("company"),
                ", ".join(job.get("skills", [])),
                job.get("location"),
                self.source_name,
                job.get("scraped_at", datetime.now().isoformat())
            ))

        conn.commit()
        conn.close()
        print(f"💾 Saved {len(jobs)} {self.source_name} jobs to database.")
