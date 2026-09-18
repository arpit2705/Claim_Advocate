"""
config.py — loads environment variables from .env using python-dotenv.
All other modules import settings from here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL: str = os.environ.get("GROQ_MODEL", "llama3-70b-8192")
EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

if not GROQ_API_KEY:
    import warnings
    warnings.warn("GROQ_API_KEY is not set. LLM calls will fail.")
