"""Predict severity of adverse drug events.

This script uses the trained model to predict the severity of adverse drug events
based on extracted medicine names and symptoms from conversations.
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path to import from other modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from extraction.medicine_extractor import MedicineExtractor
from extraction.symptom_extractor import SymptomExtractor
from matching.faers_matcher import FAERSMatcher

# Define paths
MODEL_DIR = Path("src/model")
PROCESSED_DATA_DIR = Path("data/processed")

"""
Adverse Event Prediction module.
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

class AdverseEventPredictor:
    """Class for predicting adverse events from conversations."""
    
    def __init__(self):
        """Initialize the predictor with necessary data."""
        self.data_loaded = False
        self.load_data()
        
        # Import medicine and symptom extractors
        from extraction.medicine_extractor import MedicineExtractor
        from extraction.symptom_extractor import SymptomExtractor
        
        self.medicine_extractor = MedicineExtractor()
        self.symptom_extractor = SymptomExtractor()
    
    def load_data(self):
        """Load the necessary data for prediction."""
        try:
            # Load the merged data
            merged_data_path = DATA_DIR / "merged_data.csv"
            if not merged_data_path.exists():
                logger.error(f"Merged data file not found at {merged_data_path}")
                return
            
            self.merged_data = pd.read_csv(merged_data_path, sep='|', header=None)
            self.merged_data.columns = ['id', 'case_id', 'drug', 'reaction', 'source', 'severity']
            
            # Create a mapping of drugs to their known reactions
            self.drug_reaction_map = {}
            for _, row in self.merged_data.iterrows():
                drug = row['drug'].lower()
                reaction = row['reaction'].lower()
                severity = row['severity']
                
                if drug not in self.drug_reaction_map:
                    self.drug_reaction_map[drug] = {}
                
                if reaction not in self.drug_reaction_map[drug]:
                    self.drug_reaction_map[drug][reaction] = []
                
                self.drug_reaction_map[drug][reaction].append(severity)
            
            self.data_loaded = True
            logger.info("Data loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def analyze_conversation(self, conversation_text):
        """
        Analyze a conversation for adverse events.
        
        Args:
            conversation_text (str): The text of the conversation
            
        Returns:
            dict: Analysis results including extracted medicines, symptoms, and potential adverse events
        """
        if not self.data_loaded:
            logger.warning("Data not loaded, attempting to load now")
            self.load_data()
            if not self.data_loaded:
                return {"error": "Failed to load necessary data"}
        
        # Extract medicines and symptoms
        medicines = self.medicine_extractor.extract(conversation_text)
        symptoms = self.symptom_extractor.extract(conversation_text)
        
        # Match medicines to known drugs
        adverse_events = []
        for medicine in medicines:
            # Find the best match in our drug database
            best_match = None
            best_confidence = 0
            
            for drug in self.drug_reaction_map.keys():
                # Simple string matching for now
                if medicine.lower() in drug or drug in medicine.lower():
                    confidence = len(set(medicine.lower()).intersection(set(drug))) / max(len(medicine), len(drug))
                    if confidence > best_confidence:
                        best_match = drug
                        best_confidence = confidence
            
            if best_match and best_confidence > 0.5:
                # Find matching symptoms
                matched_symptoms = []
                overall_severity = "Needs Attention"  # Default
                
                for symptom in symptoms:
                    best_symptom_match = None
                    best_symptom_confidence = 0
                    
                    for reaction in self.drug_reaction_map[best_match].keys():
                        if symptom.lower() in reaction or reaction in symptom.lower():
                            confidence = len(set(symptom.lower()).intersection(set(reaction))) / max(len(symptom), len(reaction))
                            if confidence > best_symptom_confidence:
                                best_symptom_match = reaction
                                best_symptom_confidence = confidence
                    
                    if best_symptom_match and best_symptom_confidence > 0.5:
                        # Get the most severe classification
                        severities = self.drug_reaction_map[best_match][best_symptom_match]
                        predicted_severity = max(severities, key=lambda x: 
                                               2 if "Critical" in x and "Near" not in x else 
                                               1 if "Near" in x else 0)
                        
                        matched_symptoms.append({
                            "symptom": symptom,
                            "matched_reaction": best_symptom_match,
                            "prediction_confidence": best_symptom_confidence,
                            "predicted_severity": predicted_severity
                        })
                        
                        # Update overall severity if this is more severe
                        if "Critical" in predicted_severity and "Near" not in predicted_severity:
                            overall_severity = "Critical"
                        elif "Near" in predicted_severity and overall_severity != "Critical":
                            overall_severity = "Near-Critical"
                
                if matched_symptoms:
                    adverse_events.append({
                        "medicine": medicine,
                        "matched_drug": best_match,
                        "drug_match_confidence": best_confidence,
                        "severity": overall_severity,
                        "matched_symptoms": matched_symptoms
                    })
        
        return {
            "extracted_medicines": medicines,
            "extracted_symptoms": symptoms,
            "adverse_events": adverse_events
        }
    
    def process_conversation(self, conversation_text):
        """Process a conversation to extract medicines and symptoms.
        
        Args:
            conversation_text: The conversation transcript text
            
        Returns:
            Tuple of (medicines, symptoms)
        """
        print("Processing conversation...")
        
        # Extract medicines and symptoms from the conversation
        medicines = self.medicine_extractor.extract_medicines_from_conversation(conversation_text)
        symptoms = self.symptom_extractor.extract_symptoms_from_conversation(conversation_text)
        
        print(f"Extracted {len(medicines)} medicines and {len(symptoms)} symptoms")
        return medicines, symptoms
    
    def match_with_faers(self, medicines, symptoms):
        """Match extracted medicines and symptoms with FAERS data.
        
        Args:
            medicines: List of extracted medicine names
            symptoms: List of extracted symptoms
            
        Returns:
            List of detected adverse events
        """
        print("Matching with FAERS data...")
        
        # Detect adverse events using the FAERS matcher
        adverse_events = self.faers_matcher.detect_adverse_events(medicines, symptoms)
        
        return adverse_events
    
    def predict_severity(self, medicine, symptom):
        """Predict the severity of an adverse event.
        
        Args:
            medicine: Medicine name
            symptom: Symptom text
            
        Returns:
            Predicted severity category
        """
        # Combine medicine and symptom as features
        feature = f"{medicine} {symptom}"
        
        # Make prediction
        try:
            severity = self.model.predict([feature])[0]
            probability = np.max(self.model.predict_proba([feature]))
            
            return {
                'severity': severity,
                'confidence': float(probability)
            }
        except Exception as e:
            print(f"Error predicting severity: {e}")
            return {
                'severity': 'Unknown',
                'confidence': 0.0
            }
    
    def analyze_conversation(self, conversation_text):
        """Analyze a conversation for adverse drug events.
        
        Args:
            conversation_text: The conversation transcript text
            
        Returns:
            Dictionary with analysis results
        """
        print("Analyzing conversation for adverse drug events...")
        
        # Process the conversation
        medicines, symptoms = self.process_conversation(conversation_text)
        
        # Match with FAERS data
        adverse_events = self.match_with_faers(medicines, symptoms)
        
        # Enhance with model predictions
        for event in adverse_events:
            # For each matched symptom, predict severity
            for symptom_match in event['matched_symptoms']:
                prediction = self.predict_severity(
                    event['medicine'], 
                    symptom_match['symptom']
                )
                symptom_match['predicted_severity'] = prediction['severity']
                symptom_match['prediction_confidence'] = prediction['confidence']
        
        # Prepare results
        results = {
            'extracted_medicines': medicines,
            'extracted_symptoms': symptoms,
            'adverse_events': adverse_events,
            'summary': {
                'medicine_count': len(medicines),
                'symptom_count': len(symptoms),
                'adverse_event_count': len(adverse_events)
            }
        }
        
        return results

# Example usage
def main():
    """Example usage of the AdverseEventPredictor class."""
    # Sample conversation text
    conversation = """
     Patient: I've been taking Amlodipine 5mg for my blood pressure for a few weeks, but I’ve started getting really swollen ankles.
    Doctor: I see. How long has the swelling been happening? Is it constant or does it come and go?
    Patient: It’s been getting worse over the last few days, especially after I’ve been standing for a while. It’s mostly around my ankles and calves.
    Doctor: Thank you for the details. Amlodipine can sometimes cause swelling in the legs or ankles. Are you experiencing any other symptoms, like dizziness or shortness of breath?
    Patient: I’ve been feeling a little lightheaded when I stand up quickly, but I haven’t had trouble breathing.
    Doctor: It sounds like the swelling could be a side effect of Amlodipine, and the dizziness may be from the drop in blood pressure. I think we might want to try switching to a different medication, like ACE inhibitors or ARBs, which can help manage your blood pressure without the same swelling.
    Patient: That sounds good. I’m also taking some aspirin for my heart condition and occasionally some ibuprofen for muscle pain.
    Doctor: Got it. Aspirin is fine, and we’ll make sure there are no issues with your new medication. Ibuprofen can sometimes affect kidney function, so it’s something to be mindful of while we adjust your treatment plan. We’ll keep monitoring your blood pressure and make sure we’re on the right track. How’s your heart doing otherwise?
    """
    
    try:
        # Initialize the predictor
        predictor = AdverseEventPredictor()
        
        # Analyze the conversation
        results = predictor.analyze_conversation(conversation)
        
        # Print the results
        print("\nAnalysis Results:")
        print(f"Extracted Medicines: {results['extracted_medicines']}")
        print(f"Extracted Symptoms: {results['extracted_symptoms']}")
        
        print("\nDetected Adverse Events:")
        for i, event in enumerate(results['adverse_events'], 1):
            print(f"\nAdverse Event #{i}:")
            print(f"Medicine: {event['medicine']} (matched to {event['matched_drug']})")
            print(f"FAERS Severity: {event['severity']}")
            print("Matched Symptoms:")
            for match in event['matched_symptoms']:
                print(f"  - {match['symptom']} (matched to {match['matched_reaction']})")
                print(f"    Predicted Severity: {match['predicted_severity']} (confidence: {match['prediction_confidence']:.2f})")
    
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
