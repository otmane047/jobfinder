import os

class Config:
    """Configuration générale de l'application"""
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SESSION_TYPE = "filesystem"
    DATABASE_PATH = "database.db"
    SCRAPING_INTERVAL = 1800  # Intervalle de scraping en secondes (30 min)

    # Clé de chiffrement (doit être stockée de manière sécurisée en production)
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "Xh5LcKq4btzYpHbfQbT2CNOc3qVfW6A1-sMNUvv3C0E=")

    # Configuration des plateformes de scraping
    JOB_PLATFORMS = {
        "glassdoor": "https://www.glassdoor.com/Job/france-{keyword}-jobs-SRCH_IL.0,6_IN21_KO7,{length}.htm",
        "indeed": "https://fr.indeed.com/emplois?q={keyword}&l=France",
        "monster": "https://www.monster.fr/emploi/recherche/?q={keyword}&where=France",
        "wttj": "https://www.welcometothejungle.com/fr/jobs?query={keyword}&refinementList[offices.country_code][0]=FR"
    }
