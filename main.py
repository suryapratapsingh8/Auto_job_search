# main.py
from modules.resume_parser import parse_resume, save_to_db
from modules.job_scraper.naukri_scraper import NaukriScraper
import os

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__)) # __file__ It’s a built-in variable that holds the path of the currently running file
    resume_path = os.path.join(base_dir, "data", "resume.pdf")
    output_path = os.path.join(base_dir, "output", "parsed_resume.json")

    data = parse_resume(resume_path, output_path=output_path)
    print(f"Saved JSON: {os.path.abspath(output_path)}")
    print(data)
    save_to_db(data)
    print("Saved to database")

    locations = ["India", "remote"]

    scraper = NaukriScraper(locations=locations)
    jobs = scraper.scrape()
    print(f"✅ Extracted {len(jobs)} Naukri jobs successfully!")