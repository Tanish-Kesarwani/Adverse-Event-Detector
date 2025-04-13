"""Test script for the Biomedical NER implementation.

This script tests the functionality of the biomedical NER module
to ensure it works correctly with the existing environment.
"""

import sys
import torch
from pathlib import Path
import os

# Add parent directory to path to import from other modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the biomedical NER module
from extraction.biomedical_ner import BiomedicalNER

def test_environment():
    """Test the environment to ensure all dependencies are available."""
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"Current directory: {os.getcwd()}")
    print("Environment check successful!")

def test_biomedical_ner():
    """Test the BiomedicalNER class functionality."""
    print("\nTesting BiomedicalNER implementation...")
    
    # Sample text for testing
    test_text = "Patient is taking Lisinopril 10mg for hypertension and experiencing dry cough and dizziness."
    
    try:
        # Initialize the NER system with a smaller model for testing
        # Use a smaller model that's likely already available
        ner = BiomedicalNER(model_name="dmis-lab/biobert-base-cased-v1.1")
        
        # Test entity extraction
        print("\nExtracting entities from test text...")
        entities = ner.extract_entities(test_text)
        
        print("\nExtracted entities:")
        for entity in entities:
            print(f"- {entity['text']} (Type: {entity['type']}, Confidence: {entity['score']:.2f})")
        
        # Test drug extraction
        print("\nExtracting drugs from test text...")
        drugs = ner.extract_drugs(test_text)
        
        print("\nExtracted drugs:")
        for drug in drugs:
            print(f"- {drug}")
        
        # Test symptom extraction
        print("\nExtracting symptoms from test text...")
        symptoms = ner.extract_symptoms(test_text)
        
        print("\nExtracted symptoms:")
        for symptom in symptoms:
            print(f"- {symptom}")
            
        print("\nBiomedicalNER test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing BiomedicalNER: {e}")
        return False

def main():
    """Main function to run tests."""
    print("Starting biomedical NER tests...\n")
    
    # Test environment
    test_environment()
    
    # Test BiomedicalNER
    success = test_biomedical_ner()
    
    if success:
        print("\nAll tests completed successfully!")
    else:
        print("\nTests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()