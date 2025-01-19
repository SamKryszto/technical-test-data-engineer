import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from src.etl.transform import standardize_genres, clean_duration, handle_missing_data

# Mocking the utils import to avoid the issue during tests
@pytest.fixture(autouse=True)
def mock_utils_import(monkeypatch):
    """Mock the import of etl.utils to avoid ModuleNotFoundError during testing."""
    monkeypatch.setattr("src.etl.transform.load_data_from_pickle", lambda x: None)
    monkeypatch.setattr("src.etl.transform.save_data_as_pickle", lambda x, y: None)


@pytest.fixture
def mock_tracks_df():
    """Fixture for mock tracks DataFrame."""
    return pd.DataFrame({
        'id': [1, 2],
        'name': ['Track 1', 'Track 2'],
        'genres': ['Rock', 'pop '],
        'duration': ['03:45', '04:30']
    })


@pytest.fixture
def mock_users_df():
    """Fixture for mock users DataFrame."""
    return pd.DataFrame({
        'id': [1, 2],
        'name': ['User 1', 'User 2'],
        'gender': [None, 'Male'],
        'favorite_genres': [None, 'Jazz']
    })


@pytest.fixture
def mock_listen_history_df():
    """Fixture for mock listen history DataFrame."""
    return pd.DataFrame({
        'user_id': [1, 2],
        'track_id': [1, 2],
        'timestamp': [None, pd.to_datetime('2025-01-19')],
        'created_at': [pd.to_datetime('2025-01-01'), None],
        'updated_at': [None, pd.to_datetime('2025-01-19')],
        'items': [None, ['item1', 'item2']]
    })


def test_standardize_genres(mock_tracks_df):
    """Test the standardize_genres function."""
    # Call the standardize_genres function
    result = standardize_genres(mock_tracks_df)

    # Verify that genres are standardized (lowercase and stripped)
    assert result['genres'][0] == 'rock'
    assert result['genres'][1] == 'pop'


def test_clean_duration(mock_tracks_df):
    """Test the clean_duration function."""
    # Call the clean_duration function
    result = clean_duration(mock_tracks_df)

    # Verify that durations are converted to seconds correctly
    assert result['duration_seconds'][0] == 225  # 3*60 + 45
    assert result['duration_seconds'][1] == 270  # 4*60 + 30


def test_handle_missing_data_user(mock_users_df):
    """Test the handle_missing_data function for 'user' data type."""
    # Call the handle_missing_data function
    result = handle_missing_data(mock_users_df, data_type='user')

    # Verify that missing data in gender and favorite_genres is filled with default values
    assert result['gender'][0] == 'Unknown Gender'
    assert result['favorite_genres'][0] == 'Unknown Genre'


def test_handle_missing_data_track(mock_tracks_df):
    """Test the handle_missing_data function for 'track' data type."""
    # Add missing 'duration' value
    mock_tracks_df.at[1, 'duration'] = np.nan

    # Add 'artist' column to the mock data to avoid the KeyError
    mock_tracks_df['artist'] = [None, None]  # or some default value

    # Call the handle_missing_data function for track data
    result = handle_missing_data(mock_tracks_df, data_type='track')

    # Verify that rows with missing 'duration' are dropped
    assert len(result) == 1  # Only 1 track should remain


def test_handle_missing_data_listen_history(mock_listen_history_df):
    """Test the handle_missing_data function for 'listen_history' data type."""
    # Call the handle_missing_data function for listen history
    result = handle_missing_data(mock_listen_history_df, data_type='listen_history')

    # Verify that rows with missing timestamps are dropped
    assert len(result) == 1  # Only 1 entry should remain


if __name__ == "__main__":
    pytest.main()
