import pandas as pd
import numpy as np
import logging
from etl.utils import load_data_from_pickle, save_data_as_pickle

# Set up logging for better error handling and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for date fallbacks and default values
DEFAULT_DATE = pd.to_datetime('1970-01-01')
DEFAULT_GENRE = 'Unknown Genre'
DEFAULT_GENDER = 'Unknown Gender'
DEFAULT_ARTIST = 'Unknown Artist'

def standardize_genres(dataframe):
    """Standardize genre names (e.g., lowercase and handle inconsistencies)."""
    logger.info("Standardizing genres...")
    dataframe['genres'] = dataframe['genres'].str.lower().str.strip()
    return dataframe

def clean_duration(dataframe):
    """Convert track durations from 'MM:SS' format to total seconds."""
    logger.info("Cleaning durations...")
    
    def convert_to_seconds(duration):
        try:
            minutes, seconds = map(int, duration.split(":"))
            return minutes * 60 + seconds
        except (ValueError, AttributeError):
            logger.warning(f"Invalid duration format encountered: {duration}")
            return np.nan  # If conversion fails, return NaN

    dataframe['duration_seconds'] = dataframe['duration'].apply(convert_to_seconds)
    return dataframe

def handle_missing_data(dataframe, data_type):
    """Fill missing data or remove rows with critical missing data based on data type."""
    logger.info(f"Handling missing data for {data_type}...")
    
    if data_type == 'user':
        dataframe['gender'] = dataframe['gender'].fillna(DEFAULT_GENDER)
        dataframe['favorite_genres'] = dataframe['favorite_genres'].fillna(DEFAULT_GENRE)
    elif data_type == 'track':
        dataframe['artist'] = dataframe['artist'].fillna(DEFAULT_ARTIST)
        dataframe['genres'] = dataframe['genres'].fillna(DEFAULT_GENRE)
        dataframe = dataframe.dropna(subset=['duration'])  # Drop rows with missing 'duration'
    elif data_type == 'listen_history':
        dataframe = dataframe.dropna(subset=['timestamp'])  # Drop rows with missing timestamps

    return dataframe

def normalize_track_data(dataframe):
    """Normalize track duration (optional, if needed for analytics)."""
    logger.info("Normalizing track durations...")
    
    if 'duration_seconds' in dataframe:
        max_duration = dataframe['duration_seconds'].max()
        min_duration = dataframe['duration_seconds'].min()
        # Guard against division by zero if min == max
        if max_duration != min_duration:
            dataframe['normalized_duration'] = (dataframe['duration_seconds'] - min_duration) / (max_duration - min_duration)
        else:
            dataframe['normalized_duration'] = 0  # If all values are the same, set normalized_duration to 0

    return dataframe

def text_normalization(dataframe):
    """Apply normalization to text fields such as 'name' and 'artist'."""
    logger.info("Normalizing text fields 'name' and 'artist'...")
    
    dataframe['name'] = dataframe['name'].str.strip().str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)
    dataframe['artist'] = dataframe['artist'].str.strip().str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)
    return dataframe

def transform_listen_history_data(listen_history_df):
    """Transform listen history data, including handling missing timestamps."""
    logger.info("Handling missing data for listen history...")
    
    # Convert date columns to datetime, with coercion to handle invalid dates
    listen_history_df['created_at'] = pd.to_datetime(listen_history_df['created_at'], errors='coerce').fillna(DEFAULT_DATE)
    listen_history_df['updated_at'] = pd.to_datetime(listen_history_df['updated_at'], errors='coerce').fillna(DEFAULT_DATE)
    
    # Handle 'items' field to ensure it's a list
    listen_history_df['items'] = listen_history_df['items'].apply(lambda x: x if isinstance(x, list) else [])
    
    return listen_history_df

def transform_data(tracks_df, users_df, listen_history_df):
    """
    Apply all transformations to the dataframes for tracks, users, and listen history.
    Returns transformed dataframes.
    """
    logger.info("Starting data transformation...")

    # Transform tracks data
    logger.info("Transforming tracks data...")
    tracks_df = standardize_genres(tracks_df)
    tracks_df = clean_duration(tracks_df)
    tracks_df = text_normalization(tracks_df)
    
    # Transform users data (e.g., handling missing gender and favorite genres)
    logger.info("Transforming users data...")
    users_df = handle_missing_data(users_df, data_type='user')
    
    # Transform listen history (e.g., handling missing timestamps and 'items' field)
    logger.info("Transforming listen history...")
    listen_history_df = transform_listen_history_data(listen_history_df)
    
    # Optional normalization for track data
    logger.info("Normalizing track data...")
    tracks_df = normalize_track_data(tracks_df)
    
    logger.info("Data transformation completed.")
    return tracks_df, users_df, listen_history_df

def main():
    try:
        # Load data from pickle
        logger.info("Loading data from pickle...")
        data = load_data_from_pickle('raw_data.pkl')

        # Extract the DataFrames from the loaded data
        tracks_df = data.get("tracks", pd.DataFrame())  # Default to empty DataFrame if not found
        users_df = data.get("users", pd.DataFrame())
        listen_history_df = data.get("listen_history", pd.DataFrame())
        
        # Transform data
        tracks_df, users_df, listen_history_df = transform_data(tracks_df, users_df, listen_history_df)
        
        # Save the transformed data as pickle
        data = {
            "tracks": tracks_df,
            "users": users_df,
            "listen_history": listen_history_df
        }
        logger.info("Saving transformed data as pickle file.")
        save_data_as_pickle(data, 'clean_data.pkl')

        logger.info("Transformation and saving completed.")

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        logger.debug("Exception details:", exc_info=True)

if __name__ == "__main__":
    main()
