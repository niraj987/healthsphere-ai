"""Central app configuration, loaded from environment variables (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "HealthSphere AI"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./db/healthsphere.db")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    VECTOR_STORE_HOST: str = os.getenv("VECTOR_STORE_HOST", "vector-store")
    VECTOR_STORE_PORT: int = int(os.getenv("VECTOR_STORE_PORT", "8000"))

    RXNAV_BASE_URL: str = os.getenv("RXNAV_BASE_URL", "https://rxnav.nlm.nih.gov/REST")
    OPENFDA_BASE_URL: str = os.getenv("OPENFDA_BASE_URL", "https://api.fda.gov/drug/label.json")

    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")

    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")


settings = Settings()
