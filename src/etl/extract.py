import requests
import logging
import pandas as pd
from typing import Dict
from config import API_BASE_URL
from etl.utils import save_data_as_pickle

# Set up logging for better error handling and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extract function for Tracks
def extract_tracks() -> pd.DataFrame:
    """Extract track data from the API and return as DataFrame"""
    try:
        logger.info("Fetching track data...")
        response = requests.get(f"{API_BASE_URL}/tracks")
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        tracks_data = response.json()
        logger.info(f"Successfully fetched {len(tracks_data.get('items', []))} tracks.")

        # Safely access 'items' and convert to a DataFrame
        if "items" in tracks_data:
            tracks_df = pd.DataFrame(tracks_data["items"])
        else:
            logger.error(f"Error: 'items' key not found in tracks data. Response: {tracks_data}")
            return pd.DataFrame()  # Return empty DataFrame

        return tracks_df

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching tracks: {e}")
        return pd.DataFrame()

# Extract function for Users
def extract_users() -> pd.DataFrame:
    """Extract user data from the API and return as DataFrame"""
    try:
        logger.info("Fetching user data...")
        response = requests.get(f"{API_BASE_URL}/users")
        response.raise_for_status()
        users_data = response.json()
        logger.info(f"Successfully fetched {len(users_data.get('items', []))} users.")

        if "items" in users_data:
            users_df = pd.DataFrame(users_data["items"])
        else:
            logger.error(f"Error: 'items' key not found in users data. Response: {users_data}")
            return pd.DataFrame()  # Return empty DataFrame

        return users_df

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching users: {e}")
        return pd.DataFrame()

# Extract function for Listen History
def extract_listen_history() -> pd.DataFrame:
    """Extract listen history data from the API and return as DataFrame"""
    try:
        logger.info("Fetching listen history data...")
        response = requests.get(f"{API_BASE_URL}/listen_history")
        response.raise_for_status()
        listen_history_data = response.json()
        logger.info(f"Successfully fetched {len(listen_history_data.get('items', []))} listen histories.")

        if "items" in listen_history_data:
            listen_history_df = pd.DataFrame(listen_history_data["items"])
        else:
            logger.error(f"Error: 'items' key not found in listen history data. Response: {listen_history_data}")
            return pd.DataFrame()  # Return empty DataFrame

        return listen_history_df

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching listen history: {e}")
        return pd.DataFrame()

# Orchestrating function to run all extraction steps and save the data as pickle
def extract_all_data() -> Dict[str, pd.DataFrame]:
    """Extract data from all API endpoints"""
    logger.info("Starting data extraction...")
    data = {
        "tracks": extract_tracks(),
        "users": extract_users(),
        "listen_history": extract_listen_history(),
    }
    logger.info("Data extraction completed.")
    return data

def main():
    # Extract data
    logger.info("Beginning the ETL extraction process.")
    data = extract_all_data()
    
    # Save data as pickle file for persistence
    logger.info("Saving data as pickle file.")
    save_data_as_pickle(data, 'raw_data.pkl')

    logger.info("Extraction and saving completed.")

# Ensure the script is being run directly
if __name__ == "__main__":
    main()
