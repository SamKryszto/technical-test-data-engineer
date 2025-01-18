import pickle
from typing import Dict
import pandas as pd
import logging

# Set up logging for better error handling and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_data_as_pickle(data: Dict[str, pd.DataFrame], filename: str = "data.pkl"):
    """Pickle the extracted data (DataFrames)"""
    try:
        with open(filename, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Data saved as pickle file: {filename}")
    except Exception as e:
        logger.error(f"Error saving data to pickle: {e}")

def load_data_from_pickle(filename):
    """Load data from a pickle file."""
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
        print(f"Data loaded from {filename}")
        return data
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        return {}