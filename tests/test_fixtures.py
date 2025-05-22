# tests/test_fixtures.py
import os
import pytest
from dotenv import load_dotenv
import keyring


@pytest.fixture(scope="session")
def credentials():
    """Provide test credentials with keyring and env fallback."""
    load_dotenv()
    username = keyring.get_password("teamworksams", "username")
    password = keyring.get_password("teamworksams", "password")
    if not username or not password:
        username = os.getenv("AMS_USERNAME", "test_user")
        password = os.getenv("AMS_PASSWORD", "test_password")
    return {
        "username": username,
        "password": password,
        "url": os.getenv("AMS_URL", "https://test.smartabase.com/site")
    }