"""Demo script for the enhanced Biomedical NER implementation.

This script demonstrates the improved extraction capabilities of the biomedical NER
module with a real-world medical conversation example.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from other modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the extraction modules
from extraction.medicine_extractor import MedicineExtractor
from extraction.symptom_extractor import SymptomExtractor

def main():
    """Main function to demonstrate the enhanced biomedical NER capabilities."""
    print("Demonstrating Enhanced Biomedical NER Capabilities\n")
    
    # Sample medical conversation
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
    
    print("Sample medical conversation:")
    print(conversation)
    
    # Initialize extractors with enhanced biomedical NER
    try:
        print("\n1. Initializing Medicine Extractor with enhanced biomedical NER...")
        medicine_extractor = MedicineExtractor()
        
        print("\n2. Initializing Symptom Extractor with enhanced biomedical NER...")
        symptom_extractor = SymptomExtractor()
        
        # Extract medicines
        print("\n3. Extracting medicines from conversation...")
        medicines = medicine_extractor.extract_medicines_from_conversation(conversation)
        
        print("\nExtracted Medicines:")
        if medicines:
            for medicine in medicines:
                print(f"  - {medicine}")
        else:
            print("  No medicines detected")
        
        # Extract symptoms
        print("\n4. Extracting symptoms from conversation...")
        symptoms = symptom_extractor.extract_symptoms_from_conversation(conversation)
        
        print("\nExtracted Symptoms:")
        if symptoms:
            for symptom in symptoms:
                print(f"  - {symptom}")
        else:
            print("  No symptoms detected")
        
        print("\nEnhanced Biomedical NER demonstration completed successfully!")
        
    except Exception as e:
        print(f"Error in demonstration: {e}")

if __name__ == "__main__":
    main()