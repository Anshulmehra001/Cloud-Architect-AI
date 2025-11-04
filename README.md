# Cloud Architect AI

An AI-powered web application that provides Google Cloud architecture recommendations for software projects using Google's Gemini AI.

## Features

- **AI-Powered Recommendations**: Get comprehensive Google Cloud architecture suggestions tailored to your project
- **Interactive Web Interface**: Clean, responsive web UI for easy project description input
- **Specialized Prompts**: Optimized prompts specifically designed for Google Cloud architecture guidance
- **Production Ready**: Containerized with Docker and ready for Google Cloud Run deployment
- **Comprehensive Testing**: Full test suite with automated validation

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Google Gemini API key (get one at https://aistudio.google.com/app/apikey)
- Docker (for containerized deployment)

**Note**: The app now uses `gemini-2.0-flash` by default. If your API key doesn't support this model, set `GEMINI_MODEL=gemini-1.5-pro` or another available model in your `.env` file.

### Local Development

1. **Clone and setup**:
   ```bash
   git clone https://github.com/Anshulmehra001/Cloud-Architect-AI.git
   cd Cloud-Architect-AI
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   
   Or on Windows with virtual environment:
   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

5. **Access the application**:
   Open http://localhost:8080 in your browser

### Example Project Descriptions

Copy and paste any of these into the web interface to get started:

**Example 1 - E-commerce Platform**:
```
A multi-tenant e-commerce platform with payment processing, inventory management, order tracking, and user authentication. Expected 50k daily active users with peak traffic during holiday sales. Needs real-time inventory updates, PCI compliance for payments, and integration with third-party shipping APIs. Priority: high availability and scalability.
```

**Example 2 - SaaS Task Management**:
```
A multi-tenant SaaS for task management with 100k monthly active users, real-time collaboration, file uploads up to 50MB, email notifications, and role-based access control. Prefer serverless architecture, low operational overhead, and GDPR compliance. Expect traffic spikes during work hours (9am-5pm). Needs CI/CD pipeline, staging environment, and cost control under $2000/month.
```

**Example 3 - Mobile App Backend**:
```
Backend API for a mobile fitness app with user profiles, workout tracking, social features, and push notifications. Expecting 200k monthly active users globally. Needs real-time leaderboards, image storage for profile photos, and integration with wearable devices. Requires low latency (under 200ms), offline sync capability, and compliance with health data regulations.
```

**Example 4 - Data Analytics Platform**:
```
A data analytics platform that ingests 10GB of log data daily, processes it in batch jobs, and provides dashboards for business intelligence. Needs data warehouse, ETL pipelines, scheduled batch processing, and user query interface. Support for SQL queries, data retention for 2 years, and integration with external BI tools. Cost-effective storage for historical data.
```

### Docker Deployment

1. **Build the container**:
   ```bash
   docker build -t cloud-architect-ai .
   ```

2. **Run with environment file**:
   ```bash
   docker run -p 8080:8080 --env-file .env cloud-architect-ai
   ```

3. **Or run with inline environment**:
   ```bash
   docker run -p 8080:8080 -e GEMINI_API_KEY=your_api_key_here cloud-architect-ai
   ```

### Google Cloud Run Deployment

1. **Using Cloud Build** (recommended):
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

2. **Manual deployment**:
   ```bash
   # Build and push to Container Registry
   docker build -t gcr.io/PROJECT_ID/cloud-architect-ai .
   docker push gcr.io/PROJECT_ID/cloud-architect-ai
   
   # Deploy to Cloud Run
   gcloud run deploy cloud-architect-ai \
     --image gcr.io/PROJECT_ID/cloud-architect-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --set-env-vars GEMINI_API_KEY=your_api_key_here
   ```

## API Reference

### GET /
Returns the main web interface.

### POST /generate
Generates architecture recommendations based on project description.

**Request Body**:
```json
{
  "prompt": "Your project description here"
}
```

**Success Response** (200):
```json
{
  "status": "success",
  "response": "Detailed architecture recommendation..."
}
```

**Error Response** (400/429/500/503):
```json
{
  "status": "error",
  "error": "Error message"
}
```

**Input Validation**:
- Project description must be 10-5000 characters
- Request must be valid JSON
- Content-Type must be application/json

## Architecture

The application follows a simple Flask-based architecture:

```
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface template
├── static/
│   └── style.css         # Styling and responsive design
├── test_app.py           # Comprehensive test suite
├── requirements.txt      # Python dependencies
├── Dockerfile           # Multi-stage container build
├── cloudbuild.yaml      # Google Cloud Build configuration
└── .env.example         # Environment configuration template
```

### Key Components

- **Flask Backend**: Handles HTTP requests and Gemini API integration
- **Gemini AI Integration**: Specialized prompts for Google Cloud architecture
- **Responsive Frontend**: Modern web interface with JavaScript interactivity
- **Error Handling**: Comprehensive error handling for API and validation issues
- **Production Configuration**: Gunicorn WSGI server with security best practices

## Testing

Run the test suite:
```bash
pytest test_app.py -v
```

The test suite includes:
- Route functionality tests
- API integration tests (mocked)
- Input validation tests
- Error handling tests
- End-to-end functionality tests

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key for AI recommendations | Yes | - |
| `GEMINI_MODEL` | Gemini model to use | No | `gemini-2.0-flash` |
| `SECRET_KEY` | Flask secret key (auto-generated in development) | No | `dev-secret-key` |
| `FLASK_ENV` | Flask environment (development/production) | No | `development` |
| `DEMO_MODE` | Enable demo mode with sample responses (true/false) | No | `false` |

## Security Considerations

- API keys are loaded from environment variables
- Input validation prevents malicious payloads
- Rate limiting through Gemini API quotas
- Non-root user in Docker container
- Production-ready Gunicorn configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Aniket Mehra**
- GitHub: [@Anshulmehra001](https://github.com/Anshulmehra001)
- Email: aniketmehra715@gmail.com
- Project: [Cloud-Architect-AI](https://github.com/Anshulmehra001/Cloud-Architect-AI)

## Support

For issues and questions:
1. Check the existing issues in the repository
2. Create a new issue with detailed description
3. Include error messages and environment details

## Changelog

### v1.0.0
- Initial release
- Google Cloud architecture recommendations
- Web interface with responsive design
- Docker containerization
- Google Cloud Run deployment support
- Comprehensive test suite