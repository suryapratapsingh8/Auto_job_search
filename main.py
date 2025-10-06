# main.py
from modules.resume_parser import parse_resume, save_to_db
import os

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resume_path = os.path.join(base_dir, "data", "resume.pdf")
    output_path = os.path.join(base_dir, "output", "parsed_resume.json")

    data = parse_resume(resume_path, output_path=output_path)
    print(f"Saved JSON: {os.path.abspath(output_path)}")
    print(data)
    save_to_db(data)
    print("Saved to database")