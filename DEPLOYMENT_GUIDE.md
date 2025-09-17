# 🚀 Step-by-Step Deployment Guide for Render

## Quick Deployment Steps

### 1. Prepare Your Files ✅
You already have all the necessary files:
- `app.py` - Flask application
- `Student_Engagement_Model.h5` - Trained model
- `requirements.txt` - Dependencies
- `Dockerfile` - Container configuration
- `render.yaml` - Render configuration

### 2. Create GitHub Repository

1. **Initialize Git Repository:**
   ```bash
   cd "e:\hack-a-thon-edu\online class attendence model and training ipynb\engagement-api-service"
   git init
   git add .
   git commit -m "Student Engagement Classification API for deployment"
   ```

2. **Create GitHub Repository:**
   - Go to [GitHub.com](https://github.com) and create new repository
   - Name: `student-engagement-api`
   - Description: `AI-powered student engagement classification API`
   - Public or Private (your choice)
   - Don't initialize with README (you already have one)

3. **Push to GitHub:**
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/student-engagement-api.git
   git push -u origin main
   ```

### 3. Deploy on Render

1. **Sign up/Login to Render:**
   - Go to [render.com](https://render.com)
   - Sign up or login (can use GitHub account)

2. **Create New Web Service:**
   - Click **"New"** → **"Web Service"**
   - Select **"Build and deploy from a Git repository"**
   - Click **"Connect GitHub"** (if not already connected)

3. **Configure Repository:**
   - Find your `student-engagement-api` repository
   - Click **"Connect"**

4. **Deployment Settings:**
   ```
   Name: student-engagement-api
   Environment: Docker
   Region: Oregon (US West) or closest to you
   Branch: main
   Root Directory: (leave blank)
   ```

5. **Advanced Settings:**
   - **Auto-Deploy:** Yes (recommended)
   - **Build Command:** (leave empty - Docker handles this)
   - **Start Command:** (leave empty - Docker handles this)

6. **Environment Variables** (optional but recommended):
   ```
   Key: FLASK_ENV
   Value: production
   
   Key: PORT
   Value: 5000
   ```

7. **Create Web Service:**
   - Click **"Create Web Service"**
   - Wait for deployment (5-10 minutes)

### 4. Monitor Deployment

1. **Check Deployment Logs:**
   - You'll see logs in real-time
   - Look for: "Model loaded successfully"
   - Final message: "Starting Student Engagement API service..."

2. **Get Your API URL:**
   - Once deployed, you'll get URL like: `https://student-engagement-api-xyz.onrender.com`

### 5. Test Your Deployed API

1. **Health Check:**
   ```bash
   curl https://your-app-name.onrender.com/
   ```

2. **Model Info:**
   ```bash
   curl https://your-app-name.onrender.com/model/info
   ```

3. **Run Test Script:**
   - Update `test_api.py` with your deployed URL:
   ```python
   API_BASE_URL = "https://your-app-name.onrender.com"
   ```
   - Run: `python test_api.py`

## 💰 Render Pricing Information

- **Free Tier:** Available with limitations
  - 750 hours/month
  - Sleeps after 15 minutes of inactivity
  - Takes ~30 seconds to wake up

- **Paid Plans:** Starting $7/month
  - No sleep mode
  - Better performance
  - More resources

## 🔧 Integration with Your Backend

Once deployed, update your main application:

### Backend Integration (Node.js/Express)

1. **Install axios** (if not already installed):
   ```bash
   npm install axios
   ```

2. **Create engagement service** (`backend/src/services/engagementService.js`):
   ```javascript
   const axios = require('axios');
   
   const ENGAGEMENT_API_URL = 'https://your-app-name.onrender.com';
   
   class EngagementService {
     async classifyEngagement(imageBase64) {
       try {
         const response = await axios.post(`${ENGAGEMENT_API_URL}/predict`, {
           image: imageBase64
         }, {
           timeout: 30000, // 30 seconds timeout
           headers: {
             'Content-Type': 'application/json'
           }
         });
         
         return response.data;
       } catch (error) {
         console.error('Engagement classification failed:', error.message);
         throw new Error('Engagement analysis unavailable');
       }
     }
   
     async batchClassify(imagesBase64) {
       try {
         const response = await axios.post(`${ENGAGEMENT_API_URL}/predict/batch`, {
           images: imagesBase64
         }, {
           timeout: 60000, // 60 seconds for batch
           headers: {
             'Content-Type': 'application/json'
           }
         });
         
         return response.data;
       } catch (error) {
         console.error('Batch engagement classification failed:', error.message);
         throw new Error('Batch engagement analysis unavailable');
       }
     }
   }
   
   module.exports = new EngagementService();
   ```

3. **Add to your attendance controller** (`backend/src/controllers/attendanceController.js`):
   ```javascript
   const engagementService = require('../services/engagementService');
   
   // Add new endpoint for engagement analysis
   const analyzeEngagement = async (req, res) => {
     try {
       const { studentId, classId, imageData } = req.body;
       
       // Classify engagement
       const engagementResult = await engagementService.classifyEngagement(imageData);
       
       // Save to database (create EngagementRecord model)
       const engagementRecord = new EngagementRecord({
         studentId,
         classId,
         timestamp: new Date(),
         predictedClass: engagementResult.predicted_class,
         confidence: engagementResult.confidence,
         engagementScore: engagementResult.engagement_score,
         classProbabilities: engagementResult.class_probabilities
       });
       
       await engagementRecord.save();
       
       res.json({
         success: true,
         engagement: engagementResult
       });
       
     } catch (error) {
       console.error('Engagement analysis error:', error);
       res.status(500).json({
         success: false,
         error: 'Engagement analysis failed'
       });
     }
   };
   ```

4. **Add routes** (`backend/src/routes/attendanceRoutes.js`):
   ```javascript
   router.post('/engagement/analyze', authMiddleware, analyzeEngagement);
   ```

### Frontend Integration (React)

1. **Add to your API client** (`frontend/src/lib/api.ts`):
   ```typescript
   // Add engagement analysis function
   export const analyzeStudentEngagement = async (imageBase64: string) => {
     const response = await fetch('/api/attendance/engagement/analyze', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         'Authorization': `Bearer ${getAuthToken()}`
       },
       body: JSON.stringify({
         studentId: getCurrentUserId(),
         classId: getCurrentClassId(),
         imageData: imageBase64
       })
     });
     
     if (!response.ok) {
       throw new Error('Engagement analysis failed');
     }
     
     return response.json();
   };
   ```

2. **Add engagement monitoring component**:
   ```typescript
   // In your video class component
   const [engagementData, setEngagementData] = useState(null);
   
   const captureAndAnalyzeEngagement = async () => {
     try {
       // Capture from video element
       const canvas = document.createElement('canvas');
       const video = videoRef.current;
       
       canvas.width = 224;
       canvas.height = 224;
       canvas.getContext('2d').drawImage(video, 0, 0, 224, 224);
       
       const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];
       
       // Analyze engagement
       const result = await analyzeStudentEngagement(imageBase64);
       setEngagementData(result.engagement);
       
     } catch (error) {
       console.error('Engagement analysis failed:', error);
     }
   };
   
   // Monitor engagement every 30 seconds
   useEffect(() => {
     const interval = setInterval(captureAndAnalyzeEngagement, 30000);
     return () => clearInterval(interval);
   }, []);
   ```

## 📝 Important Notes

1. **Cold Start:** Free tier apps sleep after 15 minutes of inactivity
2. **Timeout Handling:** Set appropriate timeouts (30-60 seconds)
3. **Error Handling:** Always have fallbacks if engagement analysis fails
4. **Privacy:** Ensure you have proper consent for analyzing student images
5. **Rate Limiting:** Don't overwhelm the API with too many requests

## 🔍 Troubleshooting

### Common Issues:

1. **"Model not loaded" error:**
   - Check deployment logs
   - Ensure model file was uploaded correctly
   - Restart the service

2. **Timeout errors:**
   - Increase timeout in your requests
   - Consider reducing image size
   - Check Render service status

3. **Out of memory:**
   - Upgrade Render plan
   - Optimize image preprocessing
   - Reduce batch sizes

### Getting Help:

1. Check Render service logs
2. Test with Postman or curl
3. Verify image format is correct base64
4. Check API endpoint URLs

## ✅ Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] Render account set up
- [ ] Web service configured
- [ ] Environment variables set
- [ ] Deployment successful (check logs)
- [ ] Health check endpoint working
- [ ] Model info endpoint working
- [ ] Test prediction working
- [ ] API URL documented
- [ ] Backend service integration code ready
- [ ] Frontend integration code ready

## 🎯 Next Steps After Deployment

1. **Test the API thoroughly**
2. **Integrate with your attendance system**
3. **Add engagement tracking to your database**
4. **Create engagement analytics dashboard**
5. **Set up monitoring and alerts**

Your Student Engagement Classification API is now ready for production use! 🚀