"""String-like resouces and other constants are initialized here.
"""

import datetime
from pathlib import Path
import string

# CSV header for output CSV. do not remove anything or you'll break usr's CSV's
# TODO: need to add short and long descriptions (breaking change)
CSV_HEADER = [
    "status",
    "title",
    "company",
    "location",
    "date",
    "blurb",
    "tags",
    "link",
    "id",
    "provider",
    "query",
    "locale",
    "wage",
    "remoteness",
]

LOG_LEVEL_NAMES = ["CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

MIN_DESCRIPTION_CHARS = 5  # If Job.description is less than this we fail valid.
MAX_CPU_WORKERS = 8  # Maximum num threads we use when scraping
MIN_JOBS_TO_PERFORM_SIMILARITY_SEARCH = 25  # Minimum # of jobs we need to TFIDF
MAX_BLOCK_LIST_DESC_CHARS = 150  # Maximum len of description in block_list JSON
DEFAULT_MAX_TFIDF_SIMILARITY = 0.75  # Maximum similarity between job text TFIDF

BS4_PARSER = "lxml"
T_NOW = datetime.datetime.today()  # NOTE: use today so we only compare days

PRINTABLE_STRINGS = set(string.printable)


def load_user_agents(file_path):
    """Loads user agent strings from a file, skipping comments and blank lines."""
    try:
        with open(file_path, "r") as file:
            return [
                line.strip()
                for line in file
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []


# Define the paths
USER_AGENT_LIST_FILE = Path(__file__).parent / "user_agent_list.txt"
USER_AGENT_LIST_MOBILE_FILE = Path(__file__).parent / "user_agent_list_mobile.txt"

# Load the lists
USER_AGENT_LIST = load_user_agents(USER_AGENT_LIST_FILE)
USER_AGENT_LIST_MOBILE = load_user_agents(USER_AGENT_LIST_MOBILE_FILE)

from enum import Enum


class Locale(Enum):
    """This will allow Scrapers / Filters / Main to identify the support they
    have for different domains of different websites

    Locale must be set as it defines the code implementation to use for forming
    the correct GET requests, to allow us to interact with a job-source.
    """

    CANADA_ENGLISH = 1
    CANADA_FRENCH = 2
    USA_ENGLISH = 3
    UK_ENGLISH = 4
    FRANCE_FRENCH = 5
    GERMANY_GERMAN = 6


class JobStatus(Enum):
    """Job statuses that are built-into jobfunnel
    NOTE: these are the only valid values for entries in 'status' in our CSV
    """

    UNKNOWN = 1
    NEW = 2
    ARCHIVE = 3
    INTERVIEWING = 4
    INTERVIEWED = 5
    REJECTED = 6
    ACCEPTED = 7
    DELETE = 8
    INTERESTED = 9
    APPLIED = 10
    APPLY = 11
    OLD = 12


class Remoteness(Enum):
    """What level of remoteness is a Job?"""

    UNKNOWN = 1  # NOTE: invalid state
    IN_PERSON = 2
    TEMPORARILY_REMOTE = 3  # AKA Cuz' COVID, realistically this is not remote!
    PARTIALLY_REMOTE = 4
    FULLY_REMOTE = 5
    ANY = 6
