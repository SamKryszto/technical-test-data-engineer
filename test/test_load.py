import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.etl.load import save_data_as_csv, main

# Mock data to use for testing
mock_data = {
    "df1": pd.DataFrame({"id": [1, 2], "name": ["Track 1", "Track 2"]}),
    "df2": pd.DataFrame({"id": [1, 2], "duration": [210, 180]})
}

# Test the `save_data_as_csv` function
@patch('os.makedirs')  # Mock os.makedirs to avoid creating directories
@patch('pandas.DataFrame.to_csv')  # Mock pandas to_csv method to avoid actual file I/O
def test_save_data_as_csv(mock_to_csv, mock_makedirs):
    mock_output_dir = "mock_output"
    
    # Call save_data_as_csv with mock data
    save_data_as_csv(mock_data, mock_output_dir)
    
    # Verify that os.makedirs was called (directory creation)
    mock_makedirs.assert_called_once_with(mock_output_dir)
    
    # Verify that to_csv was called for each DataFrame
    for name, df in mock_data.items():
        file_path = os.path.join(mock_output_dir, f"{name}.csv")
        mock_to_csv.assert_any_call(file_path, index=False)

# Test exception handling in save_data_as_csv (e.g., if the DataFrame is not a pd.DataFrame)
@patch('os.makedirs')  # Mock os.makedirs to avoid directory creation
@patch('pandas.DataFrame.to_csv')  # Mock pandas to_csv method to avoid file I/O
def test_save_data_as_csv_invalid_dataframe(mock_to_csv, mock_makedirs):
    # Passing a non-DataFrame object in the data dictionary
    invalid_data = {"df1": "invalid_data", "df2": mock_data["df2"]}
    
    # Call save_data_as_csv
    save_data_as_csv(invalid_data, "mock_output")
    
    # Verify that only the valid DataFrame (df2) gets saved as CSV
    mock_to_csv.assert_called_once_with(os.path.join("mock_output", "df2.csv"), index=False)

