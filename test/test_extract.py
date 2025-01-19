import pytest
from unittest.mock import patch
from src.etl.extract import extract_tracks, extract_users, extract_listen_history, fetch_paginated_data
import pandas as pd
from fastapi import HTTPException


@pytest.fixture
def mock_tracks_response():
    """Fixture to mock the tracks API response."""
    return {
        "items": [{"id": 1, "name": "Track 1"}, {"id": 2, "name": "Track 2"}]
    }


@pytest.fixture
def mock_users_response():
    """Fixture to mock the users API response."""
    return {
        "items": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]
    }


@pytest.fixture
def mock_listen_history_response():
    """Fixture to mock the listen history API response."""
    return {
        "items": [{"user_id": 1, "track_id": 1}, {"user_id": 2, "track_id": 2}]
    }


@patch('src.etl.extract.fetch_paginated_data')
def test_extract_tracks(mock_fetch, mock_tracks_response):
    """Test the extract_tracks function."""
    # Mock the response of fetch_paginated_data
    mock_fetch.return_value = mock_tracks_response
    
    # Call the extract_tracks function
    result = extract_tracks(page=1, size=100)

    # Check if the result is a DataFrame with expected columns
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'id' in result.columns
    assert 'name' in result.columns


@patch('src.etl.extract.fetch_paginated_data')
def test_extract_users(mock_fetch, mock_users_response):
    """Test the extract_users function."""
    # Mock the response of fetch_paginated_data
    mock_fetch.return_value = mock_users_response
    
    # Call the extract_users function
    result = extract_users(page=1, size=100)

    # Check if the result is a DataFrame with expected columns
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'id' in result.columns
    assert 'name' in result.columns


@patch('src.etl.extract.fetch_paginated_data')
def test_extract_listen_history(mock_fetch, mock_listen_history_response):
    """Test the extract_listen_history function."""
    # Mock the response of fetch_paginated_data
    mock_fetch.return_value = mock_listen_history_response
    
    # Call the extract_listen_history function
    result = extract_listen_history(page=1, size=100)

    # Check if the result is a DataFrame with expected columns
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'user_id' in result.columns
    assert 'track_id' in result.columns


@patch('src.etl.extract.fetch_paginated_data')
def test_fetch_paginated_data_error_handling(mock_fetch):
    """Test error handling in fetch_paginated_data function."""
    # Mock a failed response from the API
    mock_fetch.side_effect = HTTPException(status_code=500, detail="Failed to fetch data.")
    
    # Test the extract_tracks function to check if error is handled
    result = extract_tracks(page=1, size=100)
    assert result.empty  # Should return an empty DataFrame in case of error

