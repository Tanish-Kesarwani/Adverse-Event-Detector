"""
Symptom extraction module.
"""
import re
import pandas as pd
from pathlib import Path
from .biomedical_ner import BiomedicalNER

class SymptomExtractor:
    """Class for extracting symptom mentions from text."""
    
    def __init__(self, model_name="alvaroalon2/biobert_genetic_ner"):
        """Initialize the symptom extractor."""
        # Load a list of common symptoms from the merged data
        try:
            project_root = Path(__file__).resolve().parent.parent.parent
            data_path = project_root / "data" / "processed" / "merged_data.csv"
            
            if data_path.exists():
                data = pd.read_csv(data_path, sep='|', header=None)
                data.columns = ['id', 'case_id', 'drug', 'reaction', 'source', 'severity']
                self.symptom_list = data['reaction'].unique().tolist()
                self.symptom_list = [symptom.lower() for symptom in self.symptom_list]
            else:
                # Fallback to a small list of common symptoms
                self.symptom_list = [
                    "headache", "dizziness", "nausea", "fatigue", "cough",
                    "rash", "fever", "pain", "swelling", "vomiting",
                    "diarrhea", "constipation", "insomnia", "anxiety", "depression"
                ]
                
            # Initialize the biomedical NER component for enhanced extraction
            self.ner = BiomedicalNER(model_name=model_name)
            print("Enhanced biomedical NER initialized successfully for symptom extraction")
            
        except Exception as e:
            print(f"Error loading symptom list: {e}")
            # Fallback to a small list of common symptoms
            self.symptom_list = [
                "headache", "dizziness", "nausea", "fatigue", "cough",
                "rash", "fever", "pain", "swelling", "vomiting",
                "diarrhea", "constipation", "insomnia", "anxiety", "depression"
            ]
    
    def extract(self, text):
        """
        Extract symptom mentions from text.
        
        Args:
            text (str): The text to extract symptoms from
            
        Returns:
            list: List of extracted symptoms
        """
        text = text.lower()
        extracted_symptoms = []
        
        # Look for symptoms in our list
        for symptom in self.symptom_list:
            if symptom in text:
                extracted_symptoms.append(symptom)
        
        # Look for symptom mentions with patterns
        patterns = [
            r"experiencing ([a-zA-Z0-9\s\-]+)",
            r"suffering from ([a-zA-Z0-9\s\-]+)",
            r"having ([a-zA-Z0-9\s\-]+)",
            r"feel ([a-zA-Z0-9\s\-]+)",
            r"felt ([a-zA-Z0-9\s\-]+)",
            r"symptom of ([a-zA-Z0-9\s\-]+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                extracted_symptoms.append(match.strip())
        
        return list(set(extracted_symptoms))
    
    def extract_symptoms_from_conversation(self, conversation_text, confidence_threshold=0.7):
        """Extract symptoms from a conversation transcript using enhanced biomedical NER.
        
        Args:
            conversation_text: The conversation transcript text
            confidence_threshold: Minimum confidence score to include an entity
            
        Returns:
            List of extracted symptoms
        """
        try:
            # For very short conversations, just use pattern matching to save time
            if len(conversation_text.split()) < 50:
                print("Short conversation detected, using pattern-based extraction only")
                return self.extract(conversation_text)
                
            # Process the entire conversation with the biomedical NER
            print("Extracting symptom entities from conversation...")
            symptom_entities = self.ner.extract_entities_from_conversation(
                conversation_text, 
                entity_type="SYMPTOM"
            )
            
            # Also extract disease mentions as they can be symptoms in context
            print("Extracting disease entities from conversation...")
            disease_entities = self.ner.extract_entities_from_conversation(
                conversation_text, 
                entity_type="DISEASE"
            )
            
            # Filter by confidence threshold and extract just the text
            symptoms = [
                entity['text'] for entity in symptom_entities 
                if entity['score'] >= confidence_threshold
            ]
            
            diseases = [
                entity['text'] for entity in disease_entities 
                if entity['score'] >= confidence_threshold
            ]
            
            # Combine symptoms and diseases, remove duplicates
            all_symptoms = symptoms + diseases
            
            # Also use the pattern-based extraction as a fallback
            print("Applying pattern-based extraction as fallback...")
            pattern_symptoms = self.extract(conversation_text)
            
            # Combine all extracted symptoms and remove duplicates
            combined_symptoms = list(set(all_symptoms + pattern_symptoms))
            
            print(f"Extracted {len(combined_symptoms)} symptoms from conversation using enhanced biomedical NER")
            return combined_symptoms
            
        except Exception as e:
            print(f"Error extracting symptoms from conversation: {e}")
            # Fallback to pattern-based extraction
            print("Falling back to pattern-based extraction due to error")
            return self.extract(conversation_text)