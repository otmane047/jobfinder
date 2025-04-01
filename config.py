import os


class Config:
    TEMPLATES_AUTO_RELOAD = True
    """Configuration générale de l'application"""
    SECRET_KEY = os.getenv("SECRET_KEY", "jobboard")
    SESSION_TYPE = "filesystem"
    SCRAPING_INTERVAL = 1800  # Intervalle de scraping en secondes (30 min)

    # Configuration des plateformes de scraping
    JOB_PLATFORMS = {
        "linkedin": "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    }

    USERS_DIR = "./user_data"  # Directory to store user ZIP files

    @staticmethod
    def ensure_users_dir():
        if not os.path.exists(Config.USERS_DIR):
            os.makedirs(Config.USERS_DIR)
