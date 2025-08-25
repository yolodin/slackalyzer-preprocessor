# Hermes Web Dashboard

A modern, responsive web dashboard for the Hermes Communication Intelligence System. This dashboard provides real-time monitoring of AI processing, analytics visualization, and system management capabilities.

## Features

### Overview Page
- System status and health monitoring
- Key performance metrics (total processed, success rate, avg time)
- ML model availability and configuration
- Available data files management
- Quick processing actions

### Processing Page
- Real-time data processing monitoring
- Configurable processing parameters
- Live progress tracking with detailed logs
- Processing method selection (ML vs Rule-based)
- Error tracking and reporting

### Analytics Dashboard
- Intent distribution charts
- Sentiment analysis visualizations
- Most active threads tracking
- Urgent issues identification
- Recent activity feed
- Exportable analytics data

## Quick Start

### Prerequisites
- Python 3.7+
- Node.js 16+
- npm

### Easiest Method
```bash
# Start the complete Hermes system
python3 start_hermes.py
```

### Installation & Running

1. **Quick Start (Recommended)**:
   ```bash
   python3 start_hermes.py
   ```
   
   This will:
   - Check dependencies automatically
   - Install required packages
   - Set up initial data
   - Start both API and frontend servers
   - Open the dashboard at http://localhost:3000

2. **Manual Setup**:
   ```bash
   # Install Python dependencies
   pip install -r requirements_web.txt
   
   # Install Node.js dependencies
   cd web-dashboard
   npm install
   
   # Start API server (in one terminal)
   python3 web_api.py
   
   # Start frontend (in another terminal)
   cd web-dashboard
   npm run dev
   ```

3. **Access the Dashboard**:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Health: http://localhost:8000/api/health

## Usage

### Processing Data
1. Navigate to the **Processing** page
2. Select your data file from the dropdown
3. Choose processing method (ML or Rule-based)
4. Configure parameters (model type, thread limit)
5. Click "Start Processing"
6. Monitor progress in real-time

### Viewing Analytics
1. Navigate to the **Analytics Dashboard**
2. View key metrics and charts
3. Filter results by intent type
4. Export data for further analysis
5. Monitor urgent issues and high-activity threads

### Data Management
1. Upload new Slack export files via the interface
2. Use the data adapter to convert various formats
3. View file metadata and processing history

## API Endpoints

### System
- `GET /api/health` - Health check
- `GET /api/system/status` - System status and stats

### Processing
- `POST /api/processing/start` - Start processing job
- `GET /api/processing/status` - Get processing status
- `POST /api/processing/stop` - Stop processing

### Data & Analytics
- `GET /api/results` - Get processing results (paginated)
- `GET /api/analytics/summary` - Get analytics summary
- `GET /api/analytics/recent` - Get recent activity
- `GET /api/data/files` - List available data files

## Configuration

### Processing Options
- **Data File**: Choose from available JSON files
- **Processing Method**: ML or Rule-based
- **ML Model Type**: Lightweight (fast) or Full transformer
- **Thread Limit**: Limit number of threads to process

### ML Models
- **Classification**: DistilBERT (transformer) or MiniLM + Random Forest (lightweight)
- **Summarization**: BART-large-CNN (abstractive) or Sentence Embeddings (extractive)
- **Analytics**: Sentiment analysis, urgency detection, entity extraction

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   Flask API     │    │   Hermes AI     │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TailwindCSS   │    │   REST API      │    │   BERT/BART     │
│   Lucide Icons  │    │   CORS Enabled  │    │   Transformers  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Development

### Frontend Development
```bash
cd web-dashboard
npm run dev        # Start development server
npm run build      # Build for production
npm run start      # Start production server
```

### API Development
```bash
python3 web_api.py  # Start Flask development server
```

### Adding New Features
1. **Frontend**: Add new pages in `web-dashboard/pages/`
2. **API**: Add new endpoints in `web_api.py`
3. **Components**: Add reusable components in `web-dashboard/components/`

## Deployment

### Production Deployment
1. Build the frontend: `cd web-dashboard && npm run build`
2. Start the API: `python3 web_api.py`
3. Start the frontend: `cd web-dashboard && npm start`
4. Use a reverse proxy (nginx) to serve both

### Docker Deployment
```dockerfile
# Example Dockerfile structure
FROM node:16 AS frontend
WORKDIR /app
COPY web-dashboard/ .
RUN npm install && npm run build

FROM python:3.9 AS backend
WORKDIR /app
COPY . .
RUN pip install -r requirements_web.txt
COPY --from=frontend /app/dist ./web-dashboard/dist
CMD ["python3", "web_api.py"]
```

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Kill processes on ports 3000 and 8000
   lsof -ti:3000 | xargs kill
   lsof -ti:8000 | xargs kill
   ```

2. **Node.js not found**:
   - Install Node.js from https://nodejs.org/
   - Verify: `node --version && npm --version`

3. **Python dependencies missing**:
   ```bash
   pip install -r requirements_web.txt
   ```

4. **API server not starting**:
   ```bash
   # Check if port 8000 is available
   lsof -i :8000
   
   # Start with debug mode
   python3 web_api.py --debug
   ```

5. **Frontend build errors**:
   ```bash
   # Clear node modules and reinstall
   cd web-dashboard
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Issues

1. **Slow processing**:
   - Use lightweight ML models
   - Reduce thread limit
   - Check system resources

2. **Memory issues**:
   - Use CPU-only processing
   - Reduce batch sizes
   - Monitor memory usage

3. **API timeouts**:
   - Increase timeout settings
   - Process smaller batches
   - Use streaming responses

## Security Considerations

1. **API Security**:
   - Implement authentication for production
   - Use HTTPS in production
   - Validate input data

2. **Data Privacy**:
   - Ensure sensitive data is not logged
   - Implement data retention policies
   - Use secure file uploads

3. **Access Control**:
   - Restrict API access to authorized users
   - Implement rate limiting
   - Monitor for suspicious activity

## Monitoring and Logging

### Application Logs
- API server logs in console output
- Processing progress in real-time
- Error tracking and reporting

### System Monitoring
- CPU and memory usage
- Processing queue status
- API response times

### Health Checks
- API health endpoint: `/api/health`
- System status endpoint: `/api/system/status`
- Processing status endpoint: `/api/processing/status` 