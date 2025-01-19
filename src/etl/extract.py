import requests
import logging
import pandas as pd
from typing import Dict
from fastapi import HTTPException, Query
from .config import API_BASE_URL
from .utils import save_data_as_pickle

# Set up logging for better error handling and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function to handle pagination for large datasets
def fetch_paginated_data(url: str, page: int = 1, size: int = 100) -> Dict:
    """Fetch paginated data from an API endpoint."""
    try:
        params = {"page": page, "size": size}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching paginated data from {url}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data.")

# Extract function for Tracks with pagination and error handling
def extract_tracks(page: int = 1, size: int = 100) -> pd.DataFrame:
    """Extract track data from the API and return as DataFrame."""
    try:
        logger.info("Fetching track data...")
        tracks_data = fetch_paginated_data(f"{API_BASE_URL}/tracks", page, size)
        logger.info(f"Successfully fetched {len(tracks_data.get('items', []))} tracks.")
        
        if "items" in tracks_data:
            return pd.DataFrame(tracks_data["items"])
        else:
            logger.error(f"Error: 'items' key not found in tracks data. Response: {tracks_data}")
            return pd.DataFrame()  # Return empty DataFrame
    
    except HTTPException as e:
        logger.error(f"Error fetching tracks: {e.detail}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Extract function for Users with pagination and error handling
def extract_users(page: int = 1, size: int = 100) -> pd.DataFrame:
    """Extract user data from the API and return as DataFrame."""
    try:
        logger.info("Fetching user data...")
        users_data = fetch_paginated_data(f"{API_BASE_URL}/users", page, size)
        logger.info(f"Successfully fetched {len(users_data.get('items', []))} users.")
        
        if "items" in users_data:
            return pd.DataFrame(users_data["items"])
        else:
            logger.error(f"Error: 'items' key not found in users data. Response: {users_data}")
            return pd.DataFrame()  # Return empty DataFrame
    
    except HTTPException as e:
        logger.error(f"Error fetching users: {e.detail}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Extract function for Listen History with pagination and error handling
def extract_listen_history(page: int = 1, size: int = 100) -> pd.DataFrame:
    """Extract listen history data from the API and return as DataFrame."""
    try:
        logger.info("Fetching listen history data...")
        listen_history_data = fetch_paginated_data(f"{API_BASE_URL}/listen_history", page, size)
        logger.info(f"Successfully fetched {len(listen_history_data.get('items', []))} listen histories.")
        
        if "items" in listen_history_data:
            return pd.DataFrame(listen_history_data["items"])
        else:
            logger.error(f"Error: 'items' key not found in listen history data. Response: {listen_history_data}")
            return pd.DataFrame()  # Return empty DataFrame
    
    except HTTPException as e:
        logger.error(f"Error fetching listen history: {e.detail}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

# Orchestrating function to run all extraction steps and save the data as pickle
def extract_all_data(page: int = 1, size: int = 100) -> Dict[str, pd.DataFrame]:
    """Extract data from all API endpoints."""
    logger.info("Starting data extraction...")
    
    # Fetch data for tracks, users, and listen history
    tracks = extract_tracks(page, size)
    users = extract_users(page, size)
    listen_history = extract_listen_history(page, size)

    data = {
        "tracks": tracks,
        "users": users,
        "listen_history": listen_history,
    }

    logger.info("Data extraction completed.")
    return data

def main():
    # Extract data
    logger.info("Beginning the ETL extraction process.")
    data = extract_all_data(page=1, size=100)  # You can adjust page and size as needed
    
    # Save data as pickle file for persistence
    logger.info("Saving data as pickle file.")
    save_data_as_pickle(data, 'raw_data.pkl')

    logger.info("Extraction and saving completed.")

# Ensure the script is being run directly
if __name__ == "__main__":
    main()
