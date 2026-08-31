from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CleverCrest AI"
    app_env: str = "development"
    debug: bool = True

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "clevercrest_dev"
    db_user: str = "postgres"
    db_password: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    email_from: str

    frontend_url: str = "http://localhost:5173"

    auth_cookie_name: str = "clevercrest_access_token"
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"

    email_verification_token_expire_hours: int = 24
    password_reset_token_expire_minutes: int = 30
    invitation_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()