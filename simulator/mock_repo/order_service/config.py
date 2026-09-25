import os

class DatabaseConfig:
    # BUG INTRODUCED IN COMMIT e81f9a2: Pool size reduced from 25 to 5
    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))
    POOL_TIMEOUT_SECONDS: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/orders")
