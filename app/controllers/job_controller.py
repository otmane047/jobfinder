from app.services.linkedin_jobs_scrapper import LinkedInJobScraper


class JobController:
    @staticmethod
    def get_jobs(keyword):
        scraper = LinkedInJobScraper(
            keywords=keyword,
            location="France",
            max_pages=1
        )

        jobs = scraper.run()
        return jobs
