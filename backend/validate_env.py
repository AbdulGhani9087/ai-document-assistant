"""
validate_env.py -- Quick sanity-check script.
Run from the backend/ folder: python validate_env.py
"""
import sys

# Fix Windows cp1252 Unicode issues -- use ASCII-safe output
try:
    from config import settings
except Exception as e:
    print(f"[ERROR] Failed to load settings: {e}")
    sys.exit(1)

issues = []

if not settings.groq_api_key or "REPLACE" in settings.groq_api_key:
    issues.append("GROQ_API_KEY is still a placeholder -- set a real key in backend/.env")

if not settings.secret_key or "REPLACE" in settings.secret_key:
    issues.append(
        "SECRET_KEY is still a placeholder -- generate one with:\n"
        "  python -c \"import secrets; print(secrets.token_hex(32))\""
    )

# Warn if still using the old deprecated Groq model
deprecated_models = {"llama2-70b-4096", "llama3-70b-8192"}
if settings.groq_model_name in deprecated_models:
    issues.append(
        f"GROQ_MODEL_NAME='{settings.groq_model_name}' is DEPRECATED and no longer available.\n"
        "  Update to: llama-3.3-70b-versatile  (or llama-3.1-8b-instant for speed)"
    )

if issues:
    print("\n[WARNING] Environment validation found issues:\n")
    for i, msg in enumerate(issues, 1):
        print(f"  {i}. {msg}")
    print()
    sys.exit(1)
else:
    print("[OK] All required environment variables look good!")
    print(f"   Model    : {settings.groq_model_name}")
    print(f"   Embeds   : {settings.embedding_model}")
    print(f"   ChromaDB : {settings.chroma_persist_dir}")
    print(f"   DB       : {settings.database_url}")
    print(f"   CORS     : {settings.cors_origins}")
