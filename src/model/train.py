"""Train a model for adverse event severity prediction.

This script trains a supervised learning model to predict the severity of
adverse drug events based on medicine names, symptoms, and FAERS data.
"""

import pandas as pd
import numpy as np
import pickle
import time
from pathlib import Path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm

# Define paths
PROCESSED_DATA_DIR = Path("data/processed")
MODEL_DIR = Path("src/model")

# Ensure model directory exists
MODEL_DIR.mkdir(parents=True, exist_ok=True)

def load_preprocessed_data():
    """Load the preprocessed FAERS data for model training.
    
    Returns:
        DataFrame with preprocessed data
    """
    print("Loading preprocessed FAERS data...")
    try:
        # Load the merged data
        merged_data = pd.read_csv(PROCESSED_DATA_DIR / "merged_data.csv")
        print(f"Loaded {len(merged_data)} records for training")
        return merged_data
    except Exception as e:
        print(f"Error loading preprocessed data: {e}")
        return pd.DataFrame()

def prepare_training_data(merged_data, max_samples=50000):
    """Prepare the data for model training.
    
    Args:
        merged_data: DataFrame with preprocessed FAERS data
        max_samples: Maximum number of samples to use for training
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    print("Preparing training data...")
    
    # Check if severity column exists
    if 'severity' not in merged_data.columns:
        print("Error: Severity column not found in the data")
        return None, None, None, None
    
    # Clean data: Fill NaN values in drugname and pt columns
    print("Cleaning data: Handling missing values...")
    merged_data['drugname'] = merged_data['drugname'].fillna('')
    merged_data['pt'] = merged_data['pt'].fillna('')
    
    # Create feature columns
    # Combine drug name and reaction term as features
    merged_data['features'] = merged_data['drugname'] + " " + merged_data['pt']
    
    # Remove any remaining NaN values in features column
    merged_data = merged_data.dropna(subset=['features'])
    print(f"Removed rows with NaN values. Remaining rows: {len(merged_data)}")
    
    # Sample a smaller subset if the dataset is too large
    if len(merged_data) > max_samples:
        print(f"Dataset is very large ({len(merged_data)} samples). Sampling {max_samples} records for faster training.")
        merged_data = merged_data.sample(n=max_samples, random_state=42)
        print(f"Sampled dataset size: {len(merged_data)}")
    
    # Define target variable
    y = merged_data['severity']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        merged_data['features'], y, test_size=0.2, random_state=42
    )
    
    print(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")
    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):
    """Train a model for severity prediction.
    
    Args:
        X_train: Training features
        y_train: Training labels
        
    Returns:
        Trained model pipeline
    """
    print("Training severity prediction model...")
    
    # Create a pipeline with TF-IDF vectorizer and Random Forest classifier
    n_estimators = 100
    
    # Create the pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1))
    ])
    
    # Train the model with progress indicator
    print("Fitting TF-IDF vectorizer...")
    # First fit the TF-IDF vectorizer
    start_time = time.time()
    X_transformed = pipeline.named_steps['tfidf'].fit_transform(X_train)
    vectorizer_time = time.time() - start_time
    print(f"TF-IDF vectorization completed in {vectorizer_time:.2f} seconds")
    
    print("Training Random Forest classifier...")
    # Then train the classifier with progress tracking
    clf = pipeline.named_steps['clf']
    
    # Progress tracking for tree building
    start_time = time.time()
    print(f"Training Random Forest with {n_estimators} trees...")
    
    # Use verbose parameter to show progress during training
    # Set verbose=1 to show progress
    clf.verbose = 1
    
    # Train the classifier
    clf.fit(X_transformed, y_train)
    
    # Create a progress bar for visualization after training
    with tqdm(total=n_estimators, desc="Trees built", unit="tree") as pbar:
        pbar.update(n_estimators)
    
    elapsed_time = time.time() - start_time
    print(f"Model training completed in {elapsed_time:.2f} seconds")
    
    # Update the pipeline with the trained classifier
    pipeline.named_steps['clf'] = clf
    
    return pipeline

def evaluate_model(model, X_test, y_test):
    """Evaluate the trained model.
    
    Args:
        model: Trained model pipeline
        X_test: Test features
        y_test: Test labels
    """
    print("Evaluating model performance...")
    
    # Make predictions on the test set
    y_pred = model.predict(X_test)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Print confusion matrix
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

def save_model(model):
    """Save the trained model to disk.
    
    Args:
        model: Trained model pipeline
    """
    print("Saving model...")
    try:
        # Save the model to disk
        with open(MODEL_DIR / "severity_model.pkl", 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to {MODEL_DIR / 'severity_model.pkl'}")
    except Exception as e:
        print(f"Error saving model: {e}")

def main():
    """Main function to train the severity prediction model."""
    # Load preprocessed data
    merged_data = load_preprocessed_data()
    
    if merged_data.empty:
        print("Error: Could not load preprocessed data. Please run preprocess.py first.")
        return
    
    # Prepare training data with a maximum of 50,000 samples
    X_train, X_test, y_train, y_test = prepare_training_data(merged_data, max_samples=200000)
    
    if X_train is None:
        return
    
    # Train the model
    model = train_model(X_train, y_train)
    
    # Evaluate the model
    evaluate_model(model, X_test, y_test)
    
    # Save the model
    save_model(model)
    
    print("Model training and evaluation completed.")

if __name__ == "__main__":
    main()
