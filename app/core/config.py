import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "var"))
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", DATA_DIR / "chroma"))
DOCS_DIR = Path(os.getenv("DOCS_DIR", DATA_DIR / "docs"))
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "none")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")

PILOTAGE_API_CLIENT_ID = os.getenv("PILOTAGE_API_CLIENT_ID", "")
PILOTAGE_API_CLIENT_SECRET = os.getenv("PILOTAGE_API_CLIENT_SECRET", "")
