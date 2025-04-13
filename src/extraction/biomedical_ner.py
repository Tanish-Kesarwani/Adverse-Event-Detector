"""Biomedical Named Entity Recognition Module.

This module provides enhanced NER capabilities for biomedical text using
specialized pre-trained models. It supports extraction of medical entities
such as drugs, diseases, and symptoms with higher accuracy.
"""

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re
import numpy as np

class BiomedicalNER:
    """Class for biomedical named entity recognition using specialized models."""
    
    def __init__(self, model_name="alvaroalon2/biobert_genetic_ner"):
        """Initialize the biomedical NER with a specialized biomedical language model.
        
        Args:
            model_name: The name of the pre-trained model to use
                       Default is BioBERT which is fine-tuned for biomedical NER
        """
        print(f"Initializing BiomedicalNER with model: {model_name}")
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(model_name)
            
            # Set device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            print(f"Device set to use {self.device}")
            
            # Create NER pipeline with the biomedical model
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                aggregation_strategy="simple"  # Merge tokens with same entity
            )
            
            # Define common drug names and symptoms for better recognition
            self.common_drugs = [
                "lisinopril", "metformin", "atorvastatin", "losartan", "amlodipine",
                "metoprolol", "omeprazole", "albuterol", "gabapentin", "hydrochlorothiazide",
                "levothyroxine", "simvastatin", "montelukast", "sertraline", "fluoxetine"
            ]
            
            self.common_symptoms = [
                "headache", "dizziness", "nausea", "fatigue", "pain", "cough", "fever",
                "rash", "vomiting", "diarrhea", "shortness of breath", "chest pain",
                "swelling", "insomnia", "anxiety", "depression", "itching"
            ]
            
        except Exception as e:
            print(f"Error loading biomedical NER model: {e}")
            raise
    
    def preprocess_text(self, text):
        """Preprocess the input text for better extraction.
        
        Args:
            text: The input text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Replace common medical abbreviations
        medical_abbreviations = {
            'mg': ' milligrams ',
            'ml': ' milliliters ',
            'g': ' grams ',
            'mcg': ' micrograms ',
            'tabs': ' tablets ',
            'tab': ' tablet ',
            'caps': ' capsules ',
            'cap': ' capsule ',
            'inj': ' injection ',
            'soln': ' solution ',
            'susp': ' suspension ',
            'sr': ' sustained release ',
            'xr': ' extended release ',
            'prn': ' as needed ',
            'bid': ' twice daily ',
            'tid': ' three times daily ',
            'qid': ' four times daily ',
            'qd': ' once daily ',
            'po': ' by mouth ',
            'iv': ' intravenous ',
            'im': ' intramuscular ',
            'sc': ' subcutaneous '
        }
        
        for abbr, full in medical_abbreviations.items():
            text = re.sub(r'\b' + abbr + r'\b', full, text)
        
        return text
    
    def extract_entities(self, text, entity_type=None):
        """Extract biomedical entities from the given text.
        
        Args:
            text: The input text to extract entities from
            entity_type: Optional filter for specific entity types
                        (e.g., 'DRUG', 'SYMPTOM', 'DISEASE')
            
        Returns:
            List of extracted entities with their types
        """
        try:
            # Preprocess the text
            preprocessed_text = self.preprocess_text(text)
            
            # Extract entities using the NER pipeline
            entities = self.ner_pipeline(preprocessed_text)
            
            # Process and filter entities
            processed_entities = []
            for entity in entities:
                # The pipeline output format might vary, so handle different possible structures
                if 'entity_group' in entity:
                    entity_label = entity['entity_group'].split('-')[-1] if '-' in entity['entity_group'] else entity['entity_group']
                    entity_text = entity['word']
                    entity_score = entity['score']
                elif 'entity' in entity:
                    entity_label = entity['entity'].split('-')[-1] if '-' in entity['entity'] else entity['entity']
                    entity_text = entity['word']
                    entity_score = entity['score']
                else:
                    # Skip entities with unexpected format
                    continue
                
                # Filter by entity type if specified
                if entity_type and entity_label != entity_type:
                    continue
                
                processed_entities.append({
                    'text': entity_text,
                    'type': entity_label,
                    'score': entity_score
                })
            
            # Group adjacent entities of the same type
            grouped_entities = []
            current_entity = None
            
            for entity in processed_entities:
                if current_entity is None:
                    current_entity = entity.copy()
                elif (entity['type'] == current_entity['type'] and 
                      preprocessed_text.find(entity['text']) == 
                      preprocessed_text.find(current_entity['text']) + len(current_entity['text']) + 1):
                    # Merge adjacent entities of the same type
                    current_entity['text'] += " " + entity['text']
                    current_entity['score'] = (current_entity['score'] + entity['score']) / 2  # Average score
                else:
                    grouped_entities.append(current_entity)
                    current_entity = entity.copy()
            
            if current_entity:
                grouped_entities.append(current_entity)
            
            print(f"Extracted {len(grouped_entities)} biomedical entities from text")
            return grouped_entities
        
        except Exception as e:
            print(f"Error extracting biomedical entities: {e}")
            return []
    
    def extract_drugs(self, text, confidence_threshold=0.7):
        """Extract drug names from the given text.
        
        Args:
            text: The input text to extract drug names from
            confidence_threshold: Minimum confidence score to include an entity
            
        Returns:
            List of extracted drug names
        """
        entities = self.extract_entities(text, entity_type="DRUG")
        
        # Filter by confidence threshold and extract just the text
        drugs = [entity['text'] for entity in entities if entity['score'] >= confidence_threshold]
        
        # Remove duplicates and sort
        unique_drugs = sorted(list(set(drugs)))
        
        return unique_drugs
    
    def extract_symptoms(self, text, confidence_threshold=0.7):
        """Extract symptoms from the given text.
        
        Args:
            text: The input text to extract symptoms from
            confidence_threshold: Minimum confidence score to include an entity
            
        Returns:
            List of extracted symptoms
        """
        entities = self.extract_entities(text, entity_type="SYMPTOM")
        
        # Filter by confidence threshold and extract just the text
        symptoms = [entity['text'] for entity in entities if entity['score'] >= confidence_threshold]
        
        # Also include disease mentions as they can be symptoms in context
        disease_entities = self.extract_entities(text, entity_type="DISEASE")
        diseases = [entity['text'] for entity in disease_entities if entity['score'] >= confidence_threshold]
        
        # Combine symptoms and diseases, remove duplicates and sort
        all_symptoms = symptoms + diseases
        unique_symptoms = sorted(list(set(all_symptoms)))
        
        return unique_symptoms
    
    def extract_entities_from_conversation(self, conversation_text, entity_type=None):
        """Extract biomedical entities from a conversation transcript.
        
        Args:
            conversation_text: The conversation transcript text
            entity_type: Optional filter for specific entity types
            
        Returns:
            List of extracted entities
        """
        # Split conversation into sentences for better processing
        sentences = re.split(r'[.!?]\s+', conversation_text)
        
        all_entities = []
        negated_entities = set()  # Track negated entities
        
        for sentence in sentences:
            if sentence.strip():
                # Check for negation patterns before extracting entities
                sentence_lower = sentence.lower().strip()
                
                # Extract entities from the sentence
                entities = self.extract_entities(sentence, entity_type)
                
                # Check for negation patterns
                for entity in entities:
                    entity_text = entity['text'].lower()
                    
                    # Common negation patterns
                    negation_patterns = [
                        r'no\s+' + re.escape(entity_text),
                        r'not\s+' + re.escape(entity_text),
                        r'without\s+' + re.escape(entity_text),
                        r'deny\s+' + re.escape(entity_text),
                        r'denies\s+' + re.escape(entity_text),
                        r'negative\s+for\s+' + re.escape(entity_text),
                        r'free\s+of\s+' + re.escape(entity_text)
                    ]
                    
                    # Check if entity is negated in this sentence
                    is_negated = any(re.search(pattern, sentence_lower) for pattern in negation_patterns)
                    
                    if is_negated:
                        negated_entities.add((entity_text, entity['type']))
                    else:
                        all_entities.append(entity)
                
        # Group by entity text and type, taking the highest confidence score
        # but exclude negated entities
        grouped_entities = {}
        for entity in all_entities:
            key = (entity['text'].lower(), entity['type'])
            # Skip if this entity was negated in any sentence
            if key in negated_entities:
                continue
                
            if key not in grouped_entities or entity['score'] > grouped_entities[key]['score']:
                grouped_entities[key] = entity
        
        # Convert back to list and sort by type and text
        result = list(grouped_entities.values())
        result.sort(key=lambda x: (x['type'], x['text']))
        
        print(f"Extracted {len(result)} unique biomedical entities from conversation (after negation filtering)")
        return result

# Example usage
def main():
    """Example usage of the BiomedicalNER class."""
    # Sample conversation text
    conversation = """
    Patient: I've been taking Lisinopril for my blood pressure for about a month now, but I've developed this persistent dry cough that won't go away.
    Doctor: I see. How would you describe the cough? Is it worse at any particular time of day?
    Patient: It's a dry, tickling cough. It seems to be worse at night when I'm trying to sleep. I'm also feeling a bit dizzy sometimes, especially when I stand up quickly.
    Doctor: Are you experiencing any other symptoms like swelling in your ankles or feet?
    Patient: No swelling, but I have been having some headaches too. I'm not sure if that's related.
    """
    
    # Initialize the NER system
    try:
        ner = BiomedicalNER()
        
        # Extract all entities
        entities = ner.extract_entities_from_conversation(conversation)
        
        # Print the results
        print("\nExtracted Biomedical Entities:")
        for entity in entities:
            print(f"- {entity['text']} (Type: {entity['type']}, Confidence: {entity['score']:.2f})")
        
        # Extract drugs specifically
        drugs = ner.extract_drugs(conversation)
        print("\nExtracted Drugs:")
        for drug in drugs:
            print(f"- {drug}")
        
        # Extract symptoms specifically
        symptoms = ner.extract_symptoms(conversation)
        print("\nExtracted Symptoms:")
        for symptom in symptoms:
            print(f"- {symptom}")
    
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()