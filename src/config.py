from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Email Automation & Reminder System"
    database_url: str = "sqlite:///./email_automation.db"
    dry_run: bool = True
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Automation Demo"
    base_url: str = "http://localhost:8000"
    worker_interval_seconds: int = 15
    max_sends_per_minute: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
