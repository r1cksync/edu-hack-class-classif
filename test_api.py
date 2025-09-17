import requests
import base64
import json
import os
from PIL import Image
import io

# API configuration
API_BASE_URL = "http://localhost:5000"  # Change this to your deployed URL
# API_BASE_URL = "https://your-app-name.onrender.com"

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check endpoint...")
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_model_info():
    """Test model info endpoint"""
    print("Testing model info endpoint...")
    response = requests.get(f"{API_BASE_URL}/model/info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_single_prediction(image_path):
    """Test single image prediction"""
    print(f"Testing single prediction with image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return
    
    # Encode image to base64
    image_base64 = encode_image_to_base64(image_path)
    
    # Prepare request
    payload = {
        "image": image_base64
    }
    
    response = requests.post(f"{API_BASE_URL}/predict", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Predicted Class: {result['predicted_class']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Engagement Score: {result['engagement_score']}")
        print("Class Probabilities:")
        for class_name, prob in result['class_probabilities'].items():
            print(f"  {class_name}: {prob:.3f}")
    else:
        print(f"Error: {response.json()}")
    print("-" * 50)

def test_batch_prediction(image_paths):
    """Test batch prediction"""
    print(f"Testing batch prediction with {len(image_paths)} images...")
    
    # Encode all images
    images_base64 = []
    for image_path in image_paths:
        if os.path.exists(image_path):
            images_base64.append(encode_image_to_base64(image_path))
        else:
            print(f"Warning: Image not found: {image_path}")
    
    if not images_base64:
        print("No valid images found for batch prediction")
        return
    
    # Prepare request
    payload = {
        "images": images_base64
    }
    
    response = requests.post(f"{API_BASE_URL}/predict/batch", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Images: {result['total_images']}")
        print(f"Successful Predictions: {result['successful_predictions']}")
        print("\nResults:")
        for i, res in enumerate(result['results']):
            if 'error' not in res:
                print(f"  Image {i}: {res['predicted_class']} (confidence: {res['confidence']:.3f}, score: {res['engagement_score']})")
            else:
                print(f"  Image {i}: Error - {res['error']}")
    else:
        print(f"Error: {response.json()}")
    print("-" * 50)

def create_sample_test_image():
    """Create a simple test image if no real images are available"""
    # Create a simple colored image for testing
    img = Image.new('RGB', (224, 224), color='blue')
    test_path = 'test_sample.jpg'
    img.save(test_path)
    return test_path

def main():
    print("Student Engagement API Test Script")
    print("=" * 50)
    
    # Test health check
    try:
        test_health_check()
        test_model_info()
        
        # For testing, create a sample image if no real images exist
        sample_image = create_sample_test_image()
        
        # Test single prediction
        test_single_prediction(sample_image)
        
        # Test batch prediction
        test_batch_prediction([sample_image, sample_image])
        
        # Clean up
        if os.path.exists(sample_image):
            os.remove(sample_image)
            
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to API at {API_BASE_URL}")
        print("Make sure the API server is running!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()