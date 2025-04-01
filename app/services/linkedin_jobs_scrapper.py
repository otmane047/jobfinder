import random
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class LinkedInJobScraper:
    def __init__(self, keywords, location, max_pages=5):
        self.keywords = keywords
        self.location = location
        self.max_pages = max_pages
        self.jobs_data = []
        self.ua = UserAgent()
        self.request_count = 0
        self.session = requests.Session()

    def get_random_delay(self):
        """Return a random delay between requests"""
        return random.uniform(3, 8)  # Increased delay range

    def make_request(self, url, params=None):
        """Make a request with proper headers and rate limiting"""
        if self.request_count > 0 and self.request_count % 5 == 0:
            time.sleep(60)  # Longer pause every 5 requests

        time.sleep(self.get_random_delay())

        headers = {
            "User-Agent": self.ua.random,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.linkedin.com/jobs/"
        }

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=15)
            self.request_count += 1

            if response.status_code == 429:
                print("Rate limited - waiting 5 minutes before continuing...")
                time.sleep(300)  # Wait 5 minutes
                return self.make_request(url, params)  # Retry

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None

    def scrape_page(self, page):
        """Scrape a single page of LinkedIn job results"""
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

        params = {
            "keywords": self.keywords,
            "location": self.location,
            "start": page * 25,
            "f_TPR": "r86400",  # Last 24 hours
            "f_E": "2"  # Entry level (you can change this)
        }

        response = self.make_request(base_url, params)
        if not response:
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all("li")

        for job in jobs:
            try:
                job_title = job.find("h3", class_="base-search-card__title").get_text(strip=True)
                company = job.find("h4", class_="base-search-card__subtitle").get_text(strip=True)
                location = job.find("span", class_="job-search-card__location").get_text(strip=True)
                posted_time = job.find("time", class_="job-search-card__listdate") or \
                              job.find("time", class_="job-search-card__listdate--new")
                posted_time = posted_time.get_text(strip=True) if posted_time else "N/A"

                job_url = job.find("a", class_="base-card__full-link")["href"].split("?")[0]

                # Get additional details from the job page (with more cautious approach)
                if random.random() > 0.7:  # Only scrape details for 70% of jobs
                    job_details = self.scrape_job_details(job_url)
                else:
                    job_details = {
                        "Description": "Skipped to avoid rate limiting",
                        "Employment Type": "N/A",
                        "Seniority Level": "N/A",
                        "Industry": "N/A"
                    }

                job_data = {
                    "Title": job_title,
                    "Company": company,
                    "Location": location,
                    "Posted Time": posted_time,
                    "Job URL": job_url,
                    **job_details,
                    "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                self.jobs_data.append(job_data)
                print(f"Scraped: {job_title} at {company}")

            except Exception as e:
                print(f"Error processing job: {str(e)}")
                continue

        return True

    def scrape_job_details(self, job_url):
        """Scrape additional details from the individual job page"""
        details = {
            "Description": "N/A",
            "Employment Type": "N/A",
            "Seniority Level": "N/A",
            "Industry": "N/A"
        }

        response = self.make_request(job_url)
        if not response:
            return details

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get job description
        description = soup.find("div", class_="show-more-less-html__markup")
        if description:
            details["Description"] = description.get_text("\n", strip=True)

        # Get job criteria
        criteria = soup.find_all("li", class_="description__job-criteria-item")
        for item in criteria:
            try:
                key = item.find("h3").get_text(strip=True)
                value = item.find("span").get_text(strip=True)

                if "employment type" in key.lower():
                    details["Employment Type"] = value
                elif "seniority level" in key.lower():
                    details["Seniority Level"] = value
                elif "industries" in key.lower():
                    details["Industry"] = value
            except:
                continue

        return details

    def save_to_csv(self, filename="linkedin_jobs.csv"):
        df = pd.DataFrame(self.jobs_data)
        df.to_csv(filename, index=False)
        print(f"Saved {len(self.jobs_data)} jobs to {filename}")
        return df

    def run(self):
        for page in range(self.max_pages):
            print(f"\nScraping page {page + 1} of {self.max_pages}...")
            success = self.scrape_page(page)

            if not success:
                print("Stopping due to errors")
                break

            if page < self.max_pages - 1:
                wait_time = self.get_random_delay() * 2
                print(f"Waiting {wait_time:.1f} seconds before next page...")
                time.sleep(wait_time)

        data = self.save_to_csv()
        return data


if __name__ == "__main__":
    scraper = LinkedInJobScraper(
        keywords="software engineer",  # Job title to search for
        location="France",  # Location to search in
        max_pages=2  # Number of pages to scrape (25 jobs per page)
    )

    scraper.run()