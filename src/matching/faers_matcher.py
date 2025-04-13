"""FAERS Matcher Module.

This module matches extracted medicine names and symptoms with the FAERS dataset
to identify potential adverse drug events and their severity.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

# Define paths
PROCESSED_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data/processed"

class FAERSMatcher:
    """Class for matching medicines and symptoms with FAERS data."""
    
    def __init__(self, drug_reaction_mapping_file=None):
        """Initialize the FAERS matcher with preprocessed FAERS data.
        
        Args:
            drug_reaction_mapping_file: Path to the drug-reaction mapping file
                                       Default is None, which will use the default path
        """
        if drug_reaction_mapping_file is None:
            drug_reaction_mapping_file = Path(__file__).resolve().parent.parent.parent / "data/processed/drug_reaction_mapping.csv"
        
        print(f"Initializing FAERSMatcher with mapping file: {drug_reaction_mapping_file}")
        try:
            # Load the drug-reaction mapping
            self.drug_mapping = pd.read_csv(drug_reaction_mapping_file)
            
            # Convert string representations of lists to actual lists
            self.drug_mapping['reactions'] = self.drug_mapping['reactions'].apply(
                lambda x: eval(x) if isinstance(x, str) else x
            )
            self.drug_mapping['severities'] = self.drug_mapping['severities'].apply(
                lambda x: eval(x) if isinstance(x, str) else x
            )
            
            print(f"Loaded mapping with {len(self.drug_mapping)} drugs")
        except Exception as e:
            print(f"Error loading drug-reaction mapping: {e}")
            self.drug_mapping = pd.DataFrame({
                'drugname': [],
                'reactions': [], 
                'severities': [],
                'highest_severity': []
            })
    
    def normalize_text(self, text):
        """Normalize text for better matching.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', '', text).strip()
        
        return text
    
    def find_closest_match(self, medicine_name, threshold=0.8):
        """Find the closest matching drug in the FAERS data.
        
        Args:
            medicine_name: The medicine name to match
            threshold: Similarity threshold for matching (0-1)
            
        Returns:
            Tuple of (matched_drug_name, similarity_score) or (None, 0) if no match
        """
        # Normalize the input medicine name
        normalized_name = self.normalize_text(medicine_name)
        
        if not normalized_name:
            return None, 0
        
        best_match = None
        best_score = 0
        
        # Simple matching algorithm - can be improved with fuzzy matching
        for drug in self.drug_mapping['drugname']:
            normalized_drug = self.normalize_text(drug)
            
            # Check if the normalized medicine name is contained in the drug name or vice versa
            if normalized_name in normalized_drug or normalized_drug in normalized_name:
                # Calculate a simple similarity score based on length ratio
                score = min(len(normalized_name), len(normalized_drug)) / max(len(normalized_name), len(normalized_drug))
                
                if score > best_score:
                    best_score = score
                    best_match = drug
        
        # Return the best match if it meets the threshold
        if best_score >= threshold:
            return best_match, best_score
        else:
            return None, 0
    
    def match_symptom_to_reactions(self, symptom, reactions, threshold=0.7):
        """Match a symptom to reactions in the FAERS data.
        
        Args:
            symptom: The symptom to match
            reactions: List of reactions to match against
            threshold: Similarity threshold for matching (0-1)
            
        Returns:
            Tuple of (matched_reaction, similarity_score) or (None, 0) if no match
        """
        # Normalize the input symptom
        normalized_symptom = self.normalize_text(symptom)
        
        if not normalized_symptom:
            return None, 0
        
        best_match = None
        best_score = 0
        
        # Match symptom to reactions
        for reaction in reactions:
            normalized_reaction = self.normalize_text(reaction)
            
            # Check if the normalized symptom is contained in the reaction or vice versa
            if normalized_symptom in normalized_reaction or normalized_reaction in normalized_symptom:
                # Calculate a simple similarity score based on length ratio
                score = min(len(normalized_symptom), len(normalized_reaction)) / max(len(normalized_symptom), len(normalized_reaction))
                
                if score > best_score:
                    best_score = score
                    best_match = reaction
        
        # Return the best match if it meets the threshold
        if best_score >= threshold:
            return best_match, best_score
        else:
            return None, 0
    
    def detect_adverse_events(self, medicines, symptoms):
        """Detect potential adverse events from extracted medicines and symptoms.
        
        Args:
            medicines: List of extracted medicine names
            symptoms: List of extracted symptoms
            
        Returns:
            List of dictionaries containing detected adverse events with severity
        """
        print(f"Detecting adverse events for {len(medicines)} medicines and {len(symptoms)} symptoms")
        
        adverse_events = []
        
        for medicine in medicines:
            # Find the closest matching drug in FAERS
            matched_drug, drug_score = self.find_closest_match(medicine)
            
            if matched_drug is None:
                print(f"No match found for medicine: {medicine}")
                continue
            
            print(f"Matched medicine '{medicine}' to FAERS drug '{matched_drug}' with score {drug_score:.2f}")
            
            # Get the drug data from the mapping
            drug_data = self.drug_mapping[self.drug_mapping['drugname'] == matched_drug].iloc[0]
            reactions = drug_data['reactions']
            severities = drug_data['severities']
            highest_severity = drug_data['highest_severity']
            
            # Match symptoms to reactions
            matched_symptoms = []
            for symptom in symptoms:
                matched_reaction, reaction_score = self.match_symptom_to_reactions(symptom, reactions)
                
                if matched_reaction is not None:
                    print(f"  Matched symptom '{symptom}' to reaction '{matched_reaction}' with score {reaction_score:.2f}")
                    matched_symptoms.append({
                        'symptom': symptom,
                        'matched_reaction': matched_reaction,
                        'confidence': reaction_score
                    })
            
            # If we found matching symptoms, record an adverse event
            if matched_symptoms:
                adverse_event = {
                    'medicine': medicine,
                    'matched_drug': matched_drug,
                    'drug_match_confidence': drug_score,
                    'matched_symptoms': matched_symptoms,
                    'severity': highest_severity,
                    'all_possible_reactions': reactions,
                    'all_possible_severities': severities
                }
                adverse_events.append(adverse_event)
        
        print(f"Detected {len(adverse_events)} potential adverse events")
        return adverse_events

# Example usage
def main():
    """Example usage of the FAERSMatcher class."""
    # Sample extracted medicines and symptoms
    medicines = ["lisinopril", "metformin", "tylenol"]
    symptoms = ["cough", "dizziness", "headache"]
    
    try:
        # Initialize the matcher
        matcher = FAERSMatcher()
        
        # Detect adverse events
        adverse_events = matcher.detect_adverse_events(medicines, symptoms)
        
        # Print the results
        print("\nDetected Adverse Events:")
        for i, event in enumerate(adverse_events, 1):
            print(f"\nAdverse Event #{i}:")
            print(f"Medicine: {event['medicine']} (matched to {event['matched_drug']})")
            print(f"Severity: {event['severity']}")
            print("Matched Symptoms:")
            for match in event['matched_symptoms']:
                print(f"  - {match['symptom']} (matched to {match['matched_reaction']})")
    
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()