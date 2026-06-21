import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "raw_documents"
DB_DIR = DATA_DIR / "vector_db"
METADATA_FILE = DATA_DIR / "vector_db_metadata.json"

# Ensure data directories exist
DOCS_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Configuration keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "gemini-2.5-flash"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def validate_config() -> bool:
    """
    Validate that all essential credentials and paths are configured.
    Returns True if valid, False otherwise (does not print the actual key).
    """
    load_dotenv(override=True)
    key = os.getenv("GEMINI_API_KEY")
    if not key or len(key.strip()) < 10:
        return False
    return True

