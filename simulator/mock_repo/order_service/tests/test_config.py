import pytest
from order_service.config import DatabaseConfig

def test_database_pool_capacity():
    """Validates that pool size meets minimum production threshold (>= 20)."""
    assert DatabaseConfig.POOL_SIZE >= 20, (
        f"Critical Risk: DB_POOL_SIZE={DatabaseConfig.POOL_SIZE} is below minimum threshold of 20."
    )

def test_max_overflow_threshold():
    """Validates that max overflow meets minimum threshold (>= 5)."""
    assert DatabaseConfig.MAX_OVERFLOW >= 5, (
        f"Critical Risk: DB_MAX_OVERFLOW={DatabaseConfig.MAX_OVERFLOW} is below threshold of 5."
    )
