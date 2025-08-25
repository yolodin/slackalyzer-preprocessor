# 🚀 Hermes Setup & Usage Guide

## Quick Start (Recommended)

The fastest way to get Hermes running:

```bash
# Make the startup script executable
chmod +x start_hermes.py

# Start the complete system
python3 start_hermes.py
```

This will:
- ✅ Check all dependencies
- 📦 Install required packages
- 📊 Set up sample data
- 🐍 Start the API server (port 8000)
- ⚛️ Start the frontend (port 3000)
- 🌐 Open your browser automatically

---

## Prerequisites

### Required Software

1. **Python 3.7+**
   ```bash
   python3 --version  # Should be 3.7 or higher
   ```

2. **Node.js 16+**
   ```bash
   node --version     # Should be 16 or higher
   npm --version      # Should be available
   ```
   
   📥 **Install Node.js**: https://nodejs.org/

3. **Git** (for cloning the repository)
   ```bash
   git --version
   ```

---

## Installation Methods

### Method 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd Hermes

# Run the automated setup
python3 start_hermes.py
```

### Method 2: Manual Setup

```bash
# 1. Install Python dependencies
pip install -r requirements_web.txt
pip install -r requirements.txt

# 2. Install frontend dependencies
cd web-dashboard
npm install
cd ..

# 3. Start API server (Terminal 1)
python3 src/web/web_api.py

# 4. Start frontend (Terminal 2)
cd web-dashboard
npm run dev
```

### Method 3: Original Dashboard Script

```bash
# Use the existing dashboard script
python3 scripts/run_dashboard.py
```

---

## 🎯 How to Use Hermes

### 1. First Time Setup

When you first run Hermes:

1. **Add Your Slack Data**
   - Export data from your Slack workspace
   - Place JSON files in the `data/` directory
   - Supported formats: workspace exports, channel exports, thread exports

2. **Data Standardization**
   - Hermes automatically detects and converts different Slack formats
   - Creates `standardized_slack_data.json` for processing

### 2. Using the Web Dashboard

#### Main Dashboard (http://localhost:3000)
- **System Status**: Monitor processing health
- **Quick Actions**: Start processing with one click
- **ML Model Status**: Check available AI models
- **Data Files**: View and manage your Slack exports

#### Processing Page
- **Upload Data**: Add new Slack export files
- **Configure Processing**: Choose ML vs rule-based analysis
- **Real-time Monitoring**: Watch processing progress live
- **Results Download**: Export analysis results

#### Analytics Dashboard
- **Intent Distribution**: See types of conversations
- **Sentiment Analysis**: Monitor team communication mood
- **Response Times**: Track support efficiency
- **Trending Topics**: Identify common issues

### 3. Processing Your Data

#### Option A: Web Interface (Easiest)
1. Go to http://localhost:3000/processing
2. Select your data file
3. Choose processing method:
   - **ML Processing**: Higher accuracy, slower
   - **Rule-based**: Faster, good for large datasets
4. Click "Start Processing"
5. Monitor progress in real-time

#### Option B: Command Line

```bash
# Basic processing
python3 scripts/run_pipeline.py

# ML-enhanced processing
python3 scripts/run_pipeline_ml.py --use-ml

# Lightweight ML processing
python3 scripts/run_pipeline_ml.py --use-ml --lightweight

# Compare approaches
python3 scripts/run_pipeline_ml.py --compare
```

---

## 🔧 Configuration Options

### Startup Script Options

```bash
# Full system (default)
python3 start_hermes.py --mode full

# API server only
python3 start_hermes.py --mode api

# Frontend only (requires API running separately)
python3 start_hermes.py --mode frontend

# Don't open browser automatically
python3 start_hermes.py --no-browser

# Development mode with verbose output
python3 start_hermes.py --dev
```

### Processing Options

- **Data File**: Choose from available JSON files
- **Processing Method**: 
  - Rule-based (fast, 70-80% accuracy)
  - ML-based (slower, 85-95% accuracy)
- **ML Model Type**:
  - Lightweight (MiniLM + Random Forest)
  - Full Transformer (DistilBERT + BART)
- **Thread Limit**: Process subset for testing

---

## 📊 Understanding Your Results

### Intent Classifications
- **bug_report**: Technical issues and errors
- **feature_request**: Enhancement proposals
- **how_to_question**: Usage questions
- **troubleshooting**: Problem-solving conversations
- **configuration**: Setup and deployment help
- **discussion**: General team discussions
- **announcement**: Updates and notifications

### Analytics Metrics
- **Response Time**: How quickly issues get addressed
- **Resolution Rate**: Percentage of issues resolved
- **Sentiment Score**: Overall team communication mood
- **Urgency Level**: Priority assessment of conversations
- **Topic Distribution**: Most common conversation themes

---

## 🐛 Troubleshooting

### Common Issues

#### "Node.js not found"
```bash
# Install Node.js from https://nodejs.org/
# Or using package manager:
# macOS: brew install node
# Ubuntu: sudo apt install nodejs npm
```

#### "Port already in use"
```bash
# Kill processes on ports 3000 and 8000
lsof -ti:3000 | xargs kill
lsof -ti:8000 | xargs kill
```

#### "Python dependencies missing"
```bash
# Install dependencies manually
pip install flask flask-cors transformers torch scikit-learn
```

#### "API server not responding"
```bash
# Check if the API is running
curl http://localhost:8000/api/health

# Restart the API server
python3 src/web/web_api.py
```

#### "Frontend build errors"
```bash
cd web-dashboard
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Performance Issues

#### Slow ML Processing
- Use `--lightweight` flag for faster processing
- Reduce thread limit in processing options
- Process data in smaller batches

#### Memory Issues
- Use CPU-only processing: `export CUDA_VISIBLE_DEVICES=""`
- Close other applications
- Process fewer threads at once

### Getting Help

1. **Check Logs**: Console output shows detailed error messages
2. **API Health**: Visit http://localhost:8000/api/health
3. **System Status**: Check the dashboard system status
4. **Data Validation**: Review data format and file integrity

---

## 🚀 Advanced Usage

### Custom Data Processing

```bash
# Process specific file
python3 scripts/run_pipeline_ml.py --data-file data/your_file.json

# Train custom models
python3 src/slackops/train_models.py --synthetic

# Evaluate model performance
python3 src/slackops/evaluate_models.py
```

### API Integration

```bash
# Health check
curl http://localhost:8000/api/health

# Get system status
curl http://localhost:8000/api/system/status

# Start processing via API
curl -X POST http://localhost:8000/api/processing/start \
  -H "Content-Type: application/json" \
  -d '{"data_file": "data/your_file.json", "use_ml": true}'
```

### Production Deployment

```bash
# Build frontend for production
cd web-dashboard
npm run build
npm start

# Run API in production mode
export FLASK_ENV=production
python3 src/web/web_api.py
```

---

## 📁 File Structure

```
Hermes/
├── start_hermes.py           # 🚀 Main startup script
├── data/                     # 📊 Your Slack export files
├── src/
│   ├── slackops/            # 🧠 Core AI processing
│   └── web/                 # 🌐 API server
├── web-dashboard/           # ⚛️ React frontend
├── scripts/                 # 🔧 Utility scripts
├── results/                 # 📈 Processing outputs
└── reports/                 # 📋 Analytics reports
```

---

## 🎯 Next Steps

1. **Add Your Data**: Export your Slack workspace and place files in `data/`
2. **Process & Analyze**: Use the web interface to analyze your conversations
3. **Export Insights**: Download results for further analysis
4. **Customize**: Train models on your specific data
5. **Integrate**: Use the API to build custom applications

---

**🌟 Welcome to Hermes - Transform your communication data into actionable intelligence!**
