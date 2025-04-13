"""
Flask API for the MedSafeVoice Adverse Event Detection System.

This API provides endpoints for the React frontend to interact with the
adverse event detection system.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
from pathlib import Path
import time
import json
import tempfile
import uuid
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the src directory to the path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# Import the necessary modules
from model.predict import AdverseEventPredictor
from extraction.medicine_extractor import MedicineExtractor
from extraction.symptom_extractor import SymptomExtractor

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the predictor (lazy loading)
predictor = None

def get_predictor():
    """Get or initialize the adverse event predictor."""
    global predictor
    if predictor is None:
        try:
            logger.info("Initializing AdverseEventPredictor...")
            predictor = AdverseEventPredictor()
            logger.info("AdverseEventPredictor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing predictor: {e}")
            return None
    return predictor

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    """Analyze a text conversation for adverse drug events."""
    data = request.json
    conversation_text = data.get('conversation', '')
    
    if not conversation_text:
        return jsonify({'error': 'No conversation provided'}), 400
    
    # Get or initialize the predictor
    pred = get_predictor()
    if pred is None:
        return jsonify({'error': 'Failed to initialize predictor'}), 500
    
    try:
        # Process the conversation
        start_time = time.time()
        results = pred.analyze_conversation(conversation_text)
        processing_time = time.time() - start_time
        
        # Add processing metadata
        results['processing_time'] = processing_time
        results['timestamp'] = time.time()
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        return jsonify({'error': str(e)}), 500

# Add these imports at the top of your file
import whisper
import torch
from pydub import AudioSegment

@app.route('/api/analyze-audio', methods=['POST'])
def analyze_audio():
    """Analyze an audio recording for adverse drug events."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    whisper_model = request.form.get('whisper_model', 'tiny')
    enable_diarization = request.form.get('enable_diarization', 'false').lower() == 'true'
    
    # Save the audio file temporarily
    temp_dir = tempfile.gettempdir()
    file_id = str(uuid.uuid4())
    audio_path = os.path.join(temp_dir, f"{file_id}.wav")
    audio_file.save(audio_path)
    
    try:
        # Transcribe audio using Whisper
        logger.info(f"Transcribing audio with Whisper model: {whisper_model}")
        
        # Convert audio to proper format if needed
        try:
            audio = AudioSegment.from_file(audio_path)
            # Ensure it's in the right format for Whisper (16kHz mono)
            if audio.channels > 1:
                audio = audio.set_channels(1)
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
            audio.export(audio_path, format="wav")
        except Exception as e:
            logger.warning(f"Audio conversion warning: {e}")
        
        # Load Whisper model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model(whisper_model, device=device)
        
        # Transcribe
        result = model.transcribe(audio_path)
        transcription = result["text"]
        
        # Apply simple diarization if enabled (this is a basic version)
        if enable_diarization:
            # Split by sentences and alternate speakers
            sentences = [s.strip() for s in transcription.replace('?', '?|').replace('!', '!|').replace('.', '.|').split('|') if s.strip()]
            diarized_text = ""
            for i, sentence in enumerate(sentences):
                speaker = "Doctor: " if i % 2 == 0 else "Patient: "
                diarized_text += f"{speaker}{sentence}\n"
            transcription = diarized_text
        
        # Get or initialize the predictor
        pred = get_predictor()
        if pred is None:
            return jsonify({'error': 'Failed to initialize predictor'}), 500
        
        # Process the conversation
        start_time = time.time()
        results = pred.analyze_conversation(transcription)
        processing_time = time.time() - start_time
        
        # Add processing metadata and transcription details
        results['processing_time'] = processing_time
        results['timestamp'] = time.time()
        results['transcription'] = {
            'text': transcription,
            'model': whisper_model,
            'diarization_enabled': enable_diarization
        }
        
        # Clean up the temporary file
        os.remove(audio_path)
        
        return jsonify(results)
    
    except Exception as e:
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        logger.error(f"Error analyzing audio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available Whisper models and their characteristics."""
    models = [
        {
            'id': 'tiny',
            'name': 'Whisper Tiny',
            'description': 'Fastest model, lower accuracy',
            'processing_speed': 'Very Fast',
            'accuracy': 'Basic',
            'languages': 'English-focused'
        },
        {
            'id': 'base',
            'name': 'Whisper Base',
            'description': 'Good balance of speed and accuracy',
            'processing_speed': 'Fast',
            'accuracy': 'Good',
            'languages': 'Major languages'
        },
        {
            'id': 'small',
            'name': 'Whisper Small',
            'description': 'Higher accuracy, slower processing',
            'processing_speed': 'Medium',
            'accuracy': 'Very Good',
            'languages': 'Most languages'
        },
        {
            'id': 'medium',
            'name': 'Whisper Medium',
            'description': 'High accuracy, slower processing',
            'processing_speed': 'Slow',
            'accuracy': 'Excellent',
            'languages': 'All supported languages'
        }
    ]
    
    return jsonify(models)

if __name__ == '__main__':
    app.run(debug=True, port=5000)