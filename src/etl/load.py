import os
import pandas as pd
import logging
from etl.utils import load_data_from_pickle

# Set up logging for better error handling and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_data_as_csv(data, output_dir):
    """Save DataFrames from the data dictionary as CSV files."""
    try:
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        
        # Iterate over the dictionary and save each DataFrame as a CSV
        for name, df in data.items():
            if isinstance(df, pd.DataFrame):
                file_path = os.path.join(output_dir, f"{name}.csv")
                df.to_csv(file_path, index=False)
                logger.info(f"Saved {name} DataFrame as CSV to {file_path}")
            else:
                logger.warning(f"Skipping {name} as it is not a DataFrame.")
    except Exception as e:
        logger.error(f"Error saving data as CSV: {e}")

def main():
    try:
        # Load data from pickle file
        logger.info("Loading data from pickle file...")
        data = load_data_from_pickle("clean_data.pkl")

        # If data was successfully loaded, save it as CSV
        if data:
            logger.info("Data loaded successfully. Saving as CSV...")
            save_data_as_csv(data, "output_data")
        else:
            logger.warning("No data loaded from pickle file.")
            
    except Exception as e:
        logger.error(f"Error in the main execution flow: {e}")

if __name__ == "__main__":
    main()
