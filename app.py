import os
import io
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for model and class names
model = None
class_names = ['Actively Looking', 'Bored', 'Confused', 'Distracted', 'Drowsy', 'Talking to Peers']

# Model configuration
IMG_SIZE = (224, 224)
MODEL_PATH = 'Student_Engagement_Model.h5'

def load_model():
    """Load the trained model"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = keras.models.load_model(MODEL_PATH)
            logger.info(f"Model loaded successfully from {MODEL_PATH}")
            logger.info(f"Model input shape: {model.input_shape}")
            return True
        else:
            logger.error(f"Model file not found at {MODEL_PATH}")
            return False
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def preprocess_image(image_data, source_type='base64'):
    """
    Preprocess image for model prediction
    
    Args:
        image_data: Image data (base64 string or file)
        source_type: 'base64' or 'file'
    
    Returns:
        Preprocessed image array
    """
    try:
        if source_type == 'base64':
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            # Load from file-like object
            image = Image.open(image_data)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size
        image = image.resize(IMG_SIZE)
        
        # Convert to numpy array and normalize
        img_array = np.array(image)
        img_array = img_array.astype(np.float32) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise ValueError(f"Image preprocessing failed: {str(e)}")

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Student Engagement Classification API',
        'model_loaded': model is not None,
        'version': '1.0.0'
    })

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_name': 'Student Engagement Classifier',
        'input_shape': model.input_shape[1:],  # Remove batch dimension
        'output_classes': len(class_names),
        'class_names': class_names,
        'image_size': IMG_SIZE,
        'description': 'CNN model for classifying student engagement in video classes'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict student engagement from image"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Check if image data is provided
        if 'image' not in request.json:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = request.json['image']
        
        # Preprocess the image
        processed_image = preprocess_image(image_data, source_type='base64')
        
        # Make prediction
        predictions = model.predict(processed_image)
        prediction_scores = predictions[0].tolist()
        
        # Get predicted class
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = class_names[predicted_class_idx]
        confidence = float(predictions[0][predicted_class_idx])
        
        # Create response with all class probabilities
        class_probabilities = {
            class_names[i]: float(predictions[0][i]) 
            for i in range(len(class_names))
        }
        
        response = {
            'success': True,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'class_probabilities': class_probabilities,
            'engagement_score': calculate_engagement_score(class_probabilities)
        }
        
        return jsonify(response)
    
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Predict engagement for multiple images"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Check if images data is provided
        if 'images' not in request.json:
            return jsonify({'error': 'No images data provided'}), 400
        
        images_data = request.json['images']
        if not isinstance(images_data, list):
            return jsonify({'error': 'Images must be provided as a list'}), 400
        
        results = []
        
        for i, image_data in enumerate(images_data):
            try:
                # Preprocess the image
                processed_image = preprocess_image(image_data, source_type='base64')
                
                # Make prediction
                predictions = model.predict(processed_image)
                prediction_scores = predictions[0].tolist()
                
                # Get predicted class
                predicted_class_idx = np.argmax(predictions[0])
                predicted_class = class_names[predicted_class_idx]
                confidence = float(predictions[0][predicted_class_idx])
                
                # Create response with all class probabilities
                class_probabilities = {
                    class_names[j]: float(predictions[0][j]) 
                    for j in range(len(class_names))
                }
                
                result = {
                    'image_index': i,
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'class_probabilities': class_probabilities,
                    'engagement_score': calculate_engagement_score(class_probabilities)
                }
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    'image_index': i,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_images': len(images_data),
            'successful_predictions': len([r for r in results if 'error' not in r])
        })
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': 'Batch prediction failed'}), 500

def calculate_engagement_score(class_probabilities):
    """
    Calculate overall engagement score based on class probabilities
    
    Engagement levels:
    - Actively Looking: High engagement (1.0)
    - Confused: Medium engagement (0.6) - engaged but struggling
    - Talking to Peers: Medium engagement (0.5) - social engagement
    - Distracted: Low engagement (0.3)
    - Bored: Very low engagement (0.2)
    - Drowsy: Very low engagement (0.1)
    """
    engagement_weights = {
        'Actively Looking': 1.0,
        'Confused': 0.6,
        'Talking to Peers': 0.5,
        'Distracted': 0.3,
        'Bored': 0.2,
        'Drowsy': 0.1
    }
    
    score = sum(
        class_probabilities.get(class_name, 0) * weight 
        for class_name, weight in engagement_weights.items()
    )
    
    return round(score, 3)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        logger.info("Starting Student Engagement API service...")
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.error("Failed to load model. Exiting...")
        exit(1)