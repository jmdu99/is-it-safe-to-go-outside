"""Common pytest fixtures for endpoint tests."""

import uuid
import pytest


@pytest.fixture
def session_token() -> str:
    # Generate a unique session token for each test run
    return str(uuid.uuid4())


@pytest.fixture
def base_url() -> str:
    # Base URL where the API is expected to be running
    return "http://localhost:8000"
