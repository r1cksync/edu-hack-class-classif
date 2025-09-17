# Student Engagement Classification API

A Flask-based REST API service for classifying student engagement in live video classes using a trained TensorFlow/Keras CNN model.

## Features

- **Real-time Engagement Classification**: Classifies student facial expressions into 6 categories
- **Batch Processing**: Support for multiple image predictions
- **Engagement Scoring**: Calculates overall engagement score (0-1)
- **REST API**: Easy integration with web applications
- **Docker Ready**: Containerized for easy deployment
- **Render Deployment**: Pre-configured for Render cloud platform

## Classification Categories

1. **Actively Looking** - High engagement (score: 1.0)
2. **Confused** - Medium engagement (score: 0.6)
3. **Talking to Peers** - Medium engagement (score: 0.5)
4. **Distracted** - Low engagement (score: 0.3)
5. **Bored** - Very low engagement (score: 0.2)
6. **Drowsy** - Very low engagement (score: 0.1)

## API Endpoints

### Health Check
```
GET /
```
Returns API status and model loading information.

### Model Information
```
GET /model/info
```
Returns model details, input shape, and class information.

### Single Image Prediction
```
POST /predict
```
**Request Body:**
```json
{
  "image": "base64_encoded_image_string"
}
```

**Response:**
```json
{
  "success": true,
  "predicted_class": "Actively Looking",
  "confidence": 0.892,
  "engagement_score": 0.856,
  "class_probabilities": {
    "Actively Looking": 0.892,
    "Confused": 0.045,
    "Talking to Peers": 0.032,
    "Distracted": 0.021,
    "Bored": 0.008,
    "Drowsy": 0.002
  }
}
```

### Batch Prediction
```
POST /predict/batch
```
**Request Body:**
```json
{
  "images": ["base64_image_1", "base64_image_2", "..."]
}
```

**Response:**
```json
{
  "success": true,
  "total_images": 2,
  "successful_predictions": 2,
  "results": [
    {
      "image_index": 0,
      "predicted_class": "Actively Looking",
      "confidence": 0.892,
      "engagement_score": 0.856,
      "class_probabilities": {...}
    },
    {
      "image_index": 1,
      "predicted_class": "Confused",
      "confidence": 0.734,
      "engagement_score": 0.441,
      "class_probabilities": {...}
    }
  ]
}
```

## Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Test the API:
```bash
python test_api.py
```

## Deployment on Render

### Method 1: GitHub Repository (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Student engagement API"
   git branch -M main
   git remote add origin https://github.com/yourusername/student-engagement-api.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this API
   - Configure deployment settings:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
     - **Environment:** `Docker`
   - Click "Create Web Service"

### Method 2: Direct Upload

1. **Create a Render Account** at https://render.com

2. **Create New Web Service:**
   - Click "New" → "Web Service"
   - Choose "Build and deploy from a Git repository"
   - Connect GitHub and select your repository

3. **Configuration:**
   - **Name:** `student-engagement-api`
   - **Environment:** `Docker`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Build Command:** (Leave empty - Docker will handle)
   - **Start Command:** (Leave empty - Docker will handle)

4. **Environment Variables** (Optional):
   ```
   FLASK_ENV=production
   PORT=5000
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your API will be available at: `https://your-service-name.onrender.com`

### Method 3: Using render.yaml

The included `render.yaml` file provides automatic deployment configuration. Just push to a GitHub repository and connect it to Render.

## Integration with Your Backend

### Node.js/Express Example

```javascript
const axios = require('axios');
const fs = require('fs');

const ENGAGEMENT_API_URL = 'https://your-service-name.onrender.com';

async function classifyStudentEngagement(imagePath) {
  try {
    // Read and encode image
    const imageBuffer = fs.readFileSync(imagePath);
    const imageBase64 = imageBuffer.toString('base64');
    
    // Make prediction request
    const response = await axios.post(`${ENGAGEMENT_API_URL}/predict`, {
      image: imageBase64
    });
    
    return response.data;
  } catch (error) {
    console.error('Engagement classification failed:', error.message);
    throw error;
  }
}

// Usage in your attendance system
async function analyzeClassEngagement(studentImages) {
  try {
    const engagementResults = await axios.post(`${ENGAGEMENT_API_URL}/predict/batch`, {
      images: studentImages.map(img => img.base64Data)
    });
    
    // Process results
    const avgEngagementScore = engagementResults.data.results
      .filter(r => !r.error)
      .reduce((acc, r) => acc + r.engagement_score, 0) / engagementResults.data.successful_predictions;
    
    return {
      averageEngagement: avgEngagementScore,
      individualResults: engagementResults.data.results
    };
  } catch (error) {
    console.error('Batch engagement analysis failed:', error.message);
    throw error;
  }
}
```

### Frontend JavaScript Example

```javascript
// Function to capture and analyze webcam image
async function analyzeStudentEngagement() {
  try {
    // Capture image from webcam (assuming you have video element)
    const canvas = document.createElement('canvas');
    const video = document.getElementById('studentVideo');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    // Convert to base64
    const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];
    
    // Send to engagement API
    const response = await fetch('https://your-service-name.onrender.com/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageBase64 })
    });
    
    const result = await response.json();
    
    // Update UI with engagement data
    document.getElementById('engagementLevel').textContent = result.predicted_class;
    document.getElementById('engagementScore').textContent = `${(result.engagement_score * 100).toFixed(1)}%`;
    
    return result;
  } catch (error) {
    console.error('Engagement analysis failed:', error);
  }
}

// Analyze engagement every 30 seconds during class
setInterval(analyzeStudentEngagement, 30000);
```

## File Structure
```
engagement-api-service/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── render.yaml              # Render deployment config
├── test_api.py              # API testing script
├── Student_Engagement_Model.h5  # Trained model file
└── README.md                # This file
```

## Model Details

- **Architecture:** CNN with multiple convolutional and pooling layers
- **Input Size:** 224x224x3 (RGB images)
- **Framework:** TensorFlow/Keras
- **Classes:** 6 engagement categories
- **Preprocessing:** Automatic resizing and normalization

## Deployment Checklist

- [ ] Trained model file (`Student_Engagement_Model.h5`) is included
- [ ] All dependencies listed in `requirements.txt`
- [ ] Docker configuration is correct
- [ ] GitHub repository is set up
- [ ] Render account created
- [ ] Web service configured on Render
- [ ] API endpoints tested
- [ ] Integration tested with your backend

## Troubleshooting

### Common Issues:

1. **Model not loading:** Ensure `Student_Engagement_Model.h5` is in the correct directory
2. **Memory issues:** Reduce batch size or upgrade Render plan
3. **Timeout errors:** Increase timeout in gunicorn configuration
4. **Image processing errors:** Verify image is valid base64 encoded

### Logs and Monitoring:
- Check Render dashboard for deployment logs
- Use health check endpoint to verify service status
- Monitor response times and error rates

## Performance Notes

- **Startup time:** ~30-60 seconds (model loading)
- **Prediction time:** ~1-3 seconds per image
- **Batch processing:** More efficient for multiple images
- **Resource usage:** ~1GB RAM recommended

## Support

For issues or questions:
1. Check the logs in Render dashboard
2. Test locally using `test_api.py`
3. Verify model file integrity
4. Check API response format