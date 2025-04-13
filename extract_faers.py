"""Extract relevant data from FAERS datasets.

This script extracts key information from the DRUG, REAC, and OUTC datasets
from the FAERS database to be used for adverse event detection.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

# Define paths
RAW_DATA_DIR = Path("c:/Users/DIVYA DEEP/OneDrive/Desktop/Adverse-Event-Detection-System-main/data/raw")
PROCESSED_DATA_DIR = Path("c:/Users/DIVYA DEEP/OneDrive/Desktop/Adverse-Event-Detection-System-main/data/processed")

# Ensure processed directory exists
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def extract_drug_data(input_file):
    """Extract relevant columns from DRUG dataset.
    
    Args:
        input_file: Path to the DRUG dataset file
        
    Returns:
        DataFrame with extracted drug data
    """
    print(f"Extracting drug data from {input_file}")
    try:
        # Read the DRUG dataset
        # Assuming the file is in CSV format - adjust if it's a different format
        df = pd.read_csv(input_file, low_memory=False)
        
        # Extract only the columns we need
        drug_data = df[['primaryid', 'caseid', 'drugname']].copy()
        
        # Remove duplicates
        drug_data = drug_data.drop_duplicates()
        
        print(f"Extracted {len(drug_data)} drug records")
        return drug_data
    
    except Exception as e:
        print(f"Error extracting drug data: {e}")
        return pd.DataFrame()

def extract_reaction_data(input_file):
    """Extract relevant columns from REAC dataset.
    
    Args:
        input_file: Path to the REAC dataset file
        
    Returns:
        DataFrame with extracted reaction data
    """
    print(f"Extracting reaction data from {input_file}")
    try:
        # Read the REAC dataset
        df = pd.read_csv(input_file, low_memory=False)
        
        # Extract only the columns we need
        reaction_data = df[['primaryid', 'caseid', 'pt']].copy()
        
        # Remove duplicates
        reaction_data = reaction_data.drop_duplicates()
        
        print(f"Extracted {len(reaction_data)} reaction records")
        return reaction_data
    
    except Exception as e:
        print(f"Error extracting reaction data: {e}")
        return pd.DataFrame()

def extract_outcome_data(input_file):
    """Extract relevant columns from OUTC dataset.
    
    Args:
        input_file: Path to the OUTC dataset file
        
    Returns:
        DataFrame with extracted outcome data
    """
    print(f"Extracting outcome data from {input_file}")
    try:
        # Read the OUTC dataset
        df = pd.read_csv(input_file, low_memory=False)
        
        # Extract only the columns we need
        outcome_data = df[['primaryid', 'caseid', 'outc_cod']].copy()
        
        # Remove duplicates
        outcome_data = outcome_data.drop_duplicates()
        
        print(f"Extracted {len(outcome_data)} outcome records")
        return outcome_data
    
    except Exception as e:
        print(f"Error extracting outcome data: {e}")
        return pd.DataFrame()

def main():
    """Main function to extract data from FAERS datasets."""
    # Check if raw data files exist
    drug_file = RAW_DATA_DIR / "drug.csv"
    reac_file = RAW_DATA_DIR / "reac.csv"
    outc_file = RAW_DATA_DIR / "outc.csv"
    
    # Check if files exist
    files_exist = all(f.exists() for f in [drug_file, reac_file, outc_file])
    
    if not files_exist:
        print("Warning: One or more required FAERS data files not found.")
        print(f"Please ensure the following files exist in {RAW_DATA_DIR}:")
        print("- drug.csv")
        print("- reac.csv")
        print("- outc.csv")
        return
    
    # Extract data from each dataset
    drug_data = extract_drug_data(drug_file)
    reaction_data = extract_reaction_data(reac_file)
    outcome_data = extract_outcome_data(outc_file)
    
    # Save extracted data to processed directory
    if not drug_data.empty:
        drug_data.to_csv(PROCESSED_DATA_DIR / "drug_extracted.csv", index=False)
        print(f"Saved extracted drug data to {PROCESSED_DATA_DIR / 'drug_extracted.csv'}")
    
    if not reaction_data.empty:
        reaction_data.to_csv(PROCESSED_DATA_DIR / "reaction_extracted.csv", index=False)
        print(f"Saved extracted reaction data to {PROCESSED_DATA_DIR / 'reaction_extracted.csv'}")
    
    if not outcome_data.empty:
        outcome_data.to_csv(PROCESSED_DATA_DIR / "outcome_extracted.csv", index=False)
        print(f"Saved extracted outcome data to {PROCESSED_DATA_DIR / 'outcome_extracted.csv'}")
    
    print("Data extraction completed.")

if __name__ == "__main__":
    main()