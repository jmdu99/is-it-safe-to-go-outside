import uuid
import pytest

@pytest.fixture
def session_token():
    # Generate a unique session token for each test run
    return str(uuid.uuid4())

@pytest.fixture
def base_url():
    # Base URL where your API is running
    return "http://localhost:8000"
