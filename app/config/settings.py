from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

STORAGE_DIR = BASE_DIR.parent / "storage"

UPLOADS_DIR = STORAGE_DIR / "uploads"
OUTPUTS_DIR = STORAGE_DIR / "outputs"
TRANSCRIPTS_DIR = STORAGE_DIR / "transcripts"
SUMMARIES_DIR = STORAGE_DIR / "summaries"

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
