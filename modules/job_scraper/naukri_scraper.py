from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import json, os, re
from datetime import datetime
from .base_scraper import BaseScraper


class NaukriScraper(BaseScraper):
    """Scraper for Naukri.com job listings (India/Remote, 0–2 yrs, paginated)."""

    def __init__(self, locations=None, max_pages=3):
        super().__init__("Naukri")
        self.locations = locations or ["india", "remote"]
        self.max_pages = max_pages

    def _is_entry_level(self, exp_text: str) -> bool:
        exp_text = exp_text.lower()
        if "fresher" in exp_text:
            return True
        nums = [int(x) for x in re.findall(r"\d+", exp_text)]
        return any(n <= 2 for n in nums) if nums else False

    def scrape(self):
        print(f"🔍 Starting Naukri scrape for {len(self.locations)} locations...")

        all_jobs = []
        base_url = "https://www.naukri.com/jobs-in-{}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=70)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

            for loc_idx, location in enumerate(self.locations, 1):
                print(f"\n🌍 Location [{loc_idx}/{len(self.locations)}]: {location.upper()}")
                for page_num in range(1, self.max_pages + 1):
                    url = f"{base_url.format(location)}-{page_num}"
                    print(f"➡️ Page {page_num}: {url}")
                    try:
                        page.goto(url, timeout=20000)
                        page.wait_for_selector("div.cust-job-tuple.layout-wrapper", timeout=20000)

                        job_cards = page.query_selector_all("div.cust-job-tuple.layout-wrapper")
                        if not job_cards:
                            print("⚠️ No job cards found, moving to next page.")
                            break

                        for job in job_cards:
                            title_el = job.query_selector("a.title") or job.query_selector("a.title.ellipsis")
                            company_el = job.query_selector("a.comp-name") or job.query_selector("a.subTitle.ellipsis")
                            exp_el = job.query_selector("span.expwdth") or job.query_selector("li.experience")
                            loc_el = job.query_selector("span.locWdth") or job.query_selector("li.location")

                            exp_text = exp_el.inner_text().strip() if exp_el else ""
                            if not self._is_entry_level(exp_text):
                                continue

                            # Get job detail link to fetch skills
                            detail_link = title_el.get_attribute("href") if title_el else None
                            skills = []
                            if detail_link:
                                try:
                                    detail_page = browser.new_page()
                                    detail_page.goto(detail_link, timeout=15000)
                                    detail_page.wait_for_selector("div.styles_key_skill_GlPn_", timeout=10000)
                                    skill_elements = detail_page.query_selector_all("div.styles_key_skill_GlPn_ a")
                                    skills = [s.inner_text().strip() for s in skill_elements if s.inner_text().strip()]
                                    detail_page.close()
                                except PlaywrightTimeout:
                                    detail_page.close()
                                except Exception:
                                    detail_page.close()

                            job_data = {
                                "title": title_el.inner_text().strip() if title_el else None,
                                "company": company_el.inner_text().strip() if company_el else None,
                                "experience": exp_text,
                                "location": loc_el.inner_text().strip() if loc_el else location.title(),
                                "skills": skills,
                                "source": "Naukri",
                                "scraped_at": datetime.now().isoformat(),
                            }
                            all_jobs.append(job_data)

                    except PlaywrightTimeout:
                        print(f"⚠️ Timeout on page {page_num} for {location}")
                        continue
                    except Exception as e:
                        print(f"❌ Error scraping {location} page {page_num}: {e}")
                        continue

            browser.close()

        os.makedirs("data", exist_ok=True)
        json_path = os.path.join("data", "naukri_jobs.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=4)

        self.save_to_db(all_jobs)
        print(f"\n✅ Saved {len(all_jobs)} Naukri jobs (0–2 yrs only) to database.")
        return all_jobs
