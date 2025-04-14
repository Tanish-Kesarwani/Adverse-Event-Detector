# Adverse Event Detection System

## Overview

The Adverse Event Detection System is a comprehensive solution designed to help healthcare professionals identify potential adverse drug events in patient-doctor conversations. By leveraging advanced speech recognition and natural language processing technologies, the system automatically detects medications, symptoms, and their relationships to flag potential issues.


## Features

- **Audio Recording & Transcription**: Record patient-doctor conversations with automatic transcription using Whisper models
- **Speaker Diarization**: Automatically identify different speakers in the conversation
- **Medication Detection**: Advanced biomedical NER to identify medication mentions
- **Symptom Extraction**: Identify symptoms and potential adverse events
- **Relationship Analysis**: Detect relationships between medications and symptoms
- **Interactive Dashboard**: User-friendly interface for reviewing results

## System Screenshots

Here's a visual tour of our application interface:

### Home Page
![Home Page](../Adverse-Event-Detector/frontend/snapshots/page1.png)
*The landing page provides easy navigation to all system features*

### Recording Dashboard
![Recording Dashboard](../Adverse-Event-Detector/frontend/snapshots/page2.png)
*Intuitive interface for recording and configuring audio capture settings*

### Analysis Results and Transcript View
![Analysis Results](../Adverse-Event-Detector/frontend/snapshots/page3.png)
*Detailed view of extracted medications, symptoms, and potential adverse events*

![Transcript View](../Adverse-Event-Detector/frontend/snapshots/page4.png)
*Full conversation transcript with speaker identification*

### Confidence Analysis 
![Settings Panel](../Adverse-Event-Detector/frontend/snapshots/page5.png)
*Confidence analysis for medication and symptom detection*

## System Architecture

The system consists of three main components:

1. **Frontend**: React-based user interface for recording, configuration, and result visualization
2. **Backend API**: Flask server that processes audio recordings and performs analysis
3. **ML Pipeline**: Specialized models for transcription, entity extraction, and adverse event detection

```
Adverse-Event-Detection-System/
├── frontend/            # React application
├── backend/             # Flask API server
├── src/                 # Core ML components
│   ├── extraction/      # Entity extraction modules
│   ├── matching/        # Relationship detection
│   ├── model/           # ML models and prediction
│   └── data_processing/ # Data preparation utilities
└── data/                # Training and reference data
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- PyTorch 1.10+
- CUDA-compatible GPU (recommended for faster processing)

### Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Adverse-Event-Detection-System.git
cd Adverse-Event-Detection-System
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Download the required models:

```bash
python -m src.download_models
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

## Usage

### Starting the Backend Server

```bash
cd backend
python app.py
```

The backend server will start on http://localhost:5000.

### Starting the Frontend Application

```bash
cd frontend
npm start
```

The frontend application will be available at http://localhost:3000.

## Core Components

### Biomedical Named Entity Recognition

The system uses specialized biomedical NER models to identify medical entities in text:

```python
# Example of entity extraction
from src.extraction.biomedical_ner import BiomedicalNER

ner = BiomedicalNER()
entities = ner.extract_entities(text)
```

### Medicine Extraction

The <mcfile name="medicine_extractor.py" path="c:\Users\DIVYA DEEP\OneDrive\Desktop\Adverse-Event-Detection-System-main\src\extraction\medicine_extractor.py"></mcfile> module identifies medication mentions in conversations:

```python
# Example of medicine extraction
from src.extraction.medicine_extractor import MedicineExtractor

extractor = MedicineExtractor()
medicines = extractor.extract_medicines_from_conversation(conversation_text)
```

### Symptom Extraction

The <mcfile name="symptom_extractor.py" path="c:\Users\DIVYA DEEP\OneDrive\Desktop\Adverse-Event-Detection-System-main\src\extraction\symptom_extractor.py"></mcfile> module identifies symptom mentions:

```python
# Example of symptom extraction
from src.extraction.symptom_extractor import SymptomExtractor

extractor = SymptomExtractor()
symptoms = extractor.extract_symptoms_from_conversation(conversation_text)
```

## API Reference

### `/api/analyze-audio`

Analyzes an audio recording for adverse drug events.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `audio`: Audio file (WAV format)
  - `whisper_model`: Model size for transcription (tiny, base, small, medium, large)
  - `enable_diarization`: Boolean to enable speaker diarization
  - `patient_speaker`: Speaker ID for the patient (speaker1, speaker2, etc.)

**Response:**
```json
{
  "transcript": "Full conversation transcript",
  "diarization": [
    {"speaker": "speaker1", "text": "I've been taking Lisinopril...", "start": 0.0, "end": 5.2}
  ],
  "medicines": ["Lisinopril", "Metformin"],
  "symptoms": ["headache", "dizziness"],
  "adverse_events": [
    {"medicine": "Lisinopril", "symptom": "dizziness", "confidence": 0.85}
  ]
}
```

## User Interface

The system provides an intuitive user interface with the following main screens:

1. **Home Page**: Overview and navigation
2. **Recording Dashboard**: Audio recording and configuration
3. **Results Page**: Analysis results and visualization

## Advanced Configuration

The system can be configured through environment variables:

```bash
# Backend configuration
export FLASK_ENV=development
export MODEL_CACHE_DIR=./model_cache
export MAX_AUDIO_LENGTH=600  # Maximum audio length in seconds
```

## Performance Considerations

- Processing time depends on the audio length and model size
- Using a GPU significantly improves processing speed
- The "base" Whisper model offers a good balance between accuracy and speed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/transformers/) for providing pre-trained models
- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [BioBERT](https://github.com/dmis-lab/biobert) for biomedical entity recognition

## Contact

Project Link: [https://github.com/yourusername/Adverse-Event-Detection-System](https://github.com/yourusername/Adverse-Event-Detection-System)

---

*This README was last updated on April 15, 2025*