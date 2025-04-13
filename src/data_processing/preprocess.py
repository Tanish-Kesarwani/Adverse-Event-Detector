"""Preprocess extracted FAERS data for adverse event detection.

This script preprocesses the extracted FAERS data by cleaning, normalizing,
and preparing it for use in the adverse event detection model.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

# Define paths
PROCESSED_DATA_DIR = Path("data/processed")

# Define severity categories based on outcome codes
SEVERITY_CATEGORIES = {
    'Critical': ['DE', 'LT', 'HO'],  # Death, Life-Threatening, Hospitalization
    'Near-Critical': ['DS', 'CA', 'RI'],  # Disability, Congenital Anomaly, Required Intervention
    'Needs Attention': ['OT']  # Other Serious Events
}

def load_extracted_data():
    """Load the extracted FAERS data.
    
    Returns:
        Tuple of DataFrames (drug_data, reaction_data, outcome_data)
    """
    print("Loading extracted FAERS data...")
    try:
        drug_data = pd.read_csv(PROCESSED_DATA_DIR / "drug_extracted.csv")
        reaction_data = pd.read_csv(PROCESSED_DATA_DIR / "reaction_extracted.csv")
        outcome_data = pd.read_csv(PROCESSED_DATA_DIR / "outcome_extracted.csv")
        
        print(f"Loaded {len(drug_data)} drug records, {len(reaction_data)} reaction records, "
              f"and {len(outcome_data)} outcome records.")
        
        return drug_data, reaction_data, outcome_data
    
    except Exception as e:
        print(f"Error loading extracted data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def clean_drug_names(drug_data):
    """Clean and normalize drug names.
    
    Args:
        drug_data: DataFrame containing drug data
        
    Returns:
        DataFrame with cleaned drug names
    """
    print("Cleaning drug names...")
    
    # Make a copy to avoid modifying the original
    cleaned_data = drug_data.copy()
    
    # Convert to lowercase
    cleaned_data['drugname'] = cleaned_data['drugname'].str.lower()
    
    # Remove special characters and extra spaces
    cleaned_data['drugname'] = cleaned_data['drugname'].apply(
        lambda x: re.sub(r'[^\w\s]', '', str(x)).strip() if pd.notnull(x) else x
    )
    
    # Remove duplicates that might have been created after cleaning
    cleaned_data = cleaned_data.drop_duplicates()
    
    print(f"Cleaned {len(cleaned_data)} drug records")
    return cleaned_data

def clean_reaction_terms(reaction_data):
    """Clean and normalize reaction terms.
    
    Args:
        reaction_data: DataFrame containing reaction data
        
    Returns:
        DataFrame with cleaned reaction terms
    """
    print("Cleaning reaction terms...")
    
    # Make a copy to avoid modifying the original
    cleaned_data = reaction_data.copy()
    
    # Convert to lowercase
    cleaned_data['pt'] = cleaned_data['pt'].str.lower()
    
    # Remove special characters and extra spaces
    cleaned_data['pt'] = cleaned_data['pt'].apply(
        lambda x: re.sub(r'[^\w\s]', '', str(x)).strip() if pd.notnull(x) else x
    )
    
    # Remove duplicates that might have been created after cleaning
    cleaned_data = cleaned_data.drop_duplicates()
    
    print(f"Cleaned {len(cleaned_data)} reaction records")
    return cleaned_data

def categorize_severity(outcome_data):
    """Categorize outcomes by severity level.
    
    Args:
        outcome_data: DataFrame containing outcome data
        
    Returns:
        DataFrame with severity categories added
    """
    print("Categorizing outcomes by severity...")
    
    # Make a copy to avoid modifying the original
    categorized_data = outcome_data.copy()
    
    # Function to determine severity category based on outcome code
    def get_severity_category(outc_cod):
        for category, codes in SEVERITY_CATEGORIES.items():
            if outc_cod in codes:
                return category
        return 'Unknown'  # Default if no match found
    
    # Add severity category column
    categorized_data['severity'] = categorized_data['outc_cod'].apply(get_severity_category)
    
    # Count records in each severity category
    severity_counts = categorized_data['severity'].value_counts()
    print("Severity category counts:")
    for category, count in severity_counts.items():
        print(f"  {category}: {count}")
    
    return categorized_data

def merge_datasets(drug_data, reaction_data, outcome_data):
    """Merge the drug, reaction, and outcome datasets.
    
    Args:
        drug_data: DataFrame containing drug data
        reaction_data: DataFrame containing reaction data
        outcome_data: DataFrame containing outcome data
        
    Returns:
        DataFrame with merged data
    """
    print("Merging datasets...")
    
    # Merge drug and reaction data on primaryid and caseid
    merged_data = pd.merge(
        drug_data, 
        reaction_data,
        on=['primaryid', 'caseid'],
        how='inner'
    )
    
    # Merge with outcome data
    merged_data = pd.merge(
        merged_data,
        outcome_data,
        on=['primaryid', 'caseid'],
        how='left'
    )
    
    # Fill missing severity values with 'Unknown'
    if 'severity' in merged_data.columns:
        merged_data['severity'].fillna('Unknown', inplace=True)
    
    print(f"Created merged dataset with {len(merged_data)} records")
    return merged_data

def create_drug_reaction_mapping(merged_data):
    """Create a mapping of drugs to their associated reactions and severities.
    
    Args:
        merged_data: DataFrame with merged drug, reaction, and outcome data
        
    Returns:
        DataFrame with drug-reaction-severity mapping
    """
    print("Creating drug-reaction-severity mapping...")
    
    # Group by drug name and aggregate reactions and severities
    drug_mapping = merged_data.groupby('drugname').agg({
        'pt': lambda x: list(set(x)),  # Unique reactions
        'severity': lambda x: list(set(x))  # Unique severities
    }).reset_index()
    
    # Rename columns for clarity
    drug_mapping.rename(columns={
        'pt': 'reactions',
        'severity': 'severities'
    }, inplace=True)
    
    # Add highest severity column
    def get_highest_severity(severities):
        if 'Critical' in severities:
            return 'Critical'
        elif 'Near-Critical' in severities:
            return 'Near-Critical'
        elif 'Needs Attention' in severities:
            return 'Needs Attention'
        else:
            return 'Unknown'
    
    drug_mapping['highest_severity'] = drug_mapping['severities'].apply(get_highest_severity)
    
    print(f"Created drug-reaction mapping with {len(drug_mapping)} unique drugs")
    return drug_mapping

def main():
    """Main function to preprocess FAERS data."""
    # Load extracted data
    drug_data, reaction_data, outcome_data = load_extracted_data()
    
    # Check if data was loaded successfully
    if drug_data.empty or reaction_data.empty or outcome_data.empty:
        print("Error: Could not load extracted data. Please run extract_faers.py first.")
        return
    
    # Clean and normalize data
    cleaned_drug_data = clean_drug_names(drug_data)
    cleaned_reaction_data = clean_reaction_terms(reaction_data)
    categorized_outcome_data = categorize_severity(outcome_data)
    
    # Merge datasets
    merged_data = merge_datasets(cleaned_drug_data, cleaned_reaction_data, categorized_outcome_data)
    
    # Create drug-reaction mapping
    drug_reaction_mapping = create_drug_reaction_mapping(merged_data)
    
    # Save preprocessed data
    merged_data.to_csv(PROCESSED_DATA_DIR / "merged_data.csv", index=False)
    drug_reaction_mapping.to_csv(PROCESSED_DATA_DIR / "drug_reaction_mapping.csv", index=False)
    
    print("Data preprocessing completed.")
    print(f"Saved merged data to {PROCESSED_DATA_DIR / 'merged_data.csv'}")
    print(f"Saved drug-reaction mapping to {PROCESSED_DATA_DIR / 'drug_reaction_mapping.csv'}")

if __name__ == "__main__":
    main()