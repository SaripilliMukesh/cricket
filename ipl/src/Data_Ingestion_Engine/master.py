import pandas as pd
import glob
import os

def create_master_csv(year):
    # Path to the directory containing CSV files
    path = f"/home/umukesh/Desktop/cricket/ipl/data/raw/{year}/match"

    # Get all CSV files for the specified year
    csv_files = glob.glob(os.path.join(path, f"data_??_{year}.csv"))

    dfs = []  # List to store DataFrames

    for file in csv_files:
        # Extract match number from filename
        match_number = os.path.basename(file).split("_")[1]  # Extract "01" from "data_01_2023.csv"
        
        if match_number.isnumeric():  # Check if match_number is numeric
            # Read CSV file
            df = pd.read_csv(file)
            dfs.append(df)

    # Concatenate all DataFrames
    final_df = pd.concat(dfs, ignore_index=True)

    # Define the output path for the final CSV file
    output_path = f"/home/umukesh/Desktop/cricket/ipl/data/processed/{year}/master_{year}.csv"

    # Save the final DataFrame to a CSV file
    final_df.to_csv(output_path, index=False)

    print(f"Master CSV file for {year} has been saved to {output_path}")

# Example usage: to create the master CSV for the year 2024
create_master_csv(2025)
