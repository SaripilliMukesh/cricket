import pandas as pd
import glob
import os

def combine_csvs_in_processed(directory):
    # List to store DataFrames
    dfs = []

    # Walk through all subdirectories in the given directory
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            # Check if the file is a CSV
            if filename.endswith('.csv'):
                file_path = os.path.join(foldername, filename)
                # Read the CSV file and append to the list
                df = pd.read_csv(file_path)
                dfs.append(df)

    # Concatenate all DataFrames into one
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        # Define the output path for the combined CSV file
        output_path = os.path.join(directory, "cbc_master.csv")
        # Save the combined DataFrame to a CSV file
        combined_df.to_csv(output_path, index=False)
        print(f"Combined CSV file has been saved to {output_path}")
    else:
        print("No CSV files found in the specified directory.")

# Example usage: Combine all CSV files within the processed directory
combine_csvs_in_processed("/home/umukesh/Desktop/cricket/ipl/data/processed")
