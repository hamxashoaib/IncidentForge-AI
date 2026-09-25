from .config import DatabaseConfig

def get_connection_settings():
    return {
        "pool_size": DatabaseConfig.POOL_SIZE,
        "max_overflow": DatabaseConfig.MAX_OVERFLOW,
        "timeout": DatabaseConfig.POOL_TIMEOUT_SECONDS
    }
