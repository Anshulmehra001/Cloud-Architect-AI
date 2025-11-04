# Cloud Architect AI Flask Application
import os
import time
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(override=True)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
DEMO_MODE = os.environ.get('DEMO_MODE', '').lower() in ('true', '1', 'yes')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')  # Updated to latest model

if GEMINI_API_KEY and not DEMO_MODE:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
else:
    model = None

# Specialized prompt template for Google Cloud architecture recommendations
ARCHITECTURE_PROMPT_TEMPLATE = """
You are an expert Google Cloud Architect. Analyze the following software project description and provide a comprehensive Google Cloud architecture recommendation.

Project Description: {project_description}

Please provide:
1. Recommended Google Cloud services and their specific configurations
2. Architecture diagram description or component relationships
3. Scalability considerations and best practices
4. Cost optimization suggestions
5. Security recommendations
6. Deployment strategy

Focus on practical, actionable recommendations that follow Google Cloud best practices. Structure your response clearly with headings and bullet points for easy reading.
"""

def _generate_with_retry(prompt: str, max_retries: int = 2):
    """
    Call Gemini with simple exponential backoff for transient rate/quota errors.
    Returns (success: bool, text: str|None, error: str|None, rate_limited: bool)
    """
    # Demo mode: return sample response
    if DEMO_MODE:
        demo_response = """
# Google Cloud Architecture Recommendation

## Recommended Services
- **Cloud Run**: Serverless container platform for your SaaS application
- **Cloud SQL (PostgreSQL)**: Managed relational database with high availability
- **Cloud Storage**: Object storage for file uploads and static assets
- **Cloud Pub/Sub**: Message queue for email notifications and async tasks
- **Cloud CDN**: Content delivery network for global performance
- **Identity Platform**: Authentication and user management with RBAC

## Architecture Overview
```
Internet → Cloud CDN → Cloud Load Balancer
                          ↓
                    Cloud Run (Auto-scaling)
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
    Cloud SQL       Cloud Storage      Pub/Sub
    (Primary DB)    (File Storage)   (Async Tasks)
```

## Scalability Considerations
1. **Auto-scaling**: Cloud Run scales 0→N based on traffic (handles work-hour spikes)
2. **Read replicas**: Add Cloud SQL read replicas for query performance
3. **Connection pooling**: Use Cloud SQL Proxy with connection limits
4. **Caching**: Implement Cloud Memorystore (Redis) for session/data caching
5. **Multi-region**: Deploy in multiple regions for global users

## Cost Optimization
1. **Pay-per-use**: Cloud Run charges only for actual request time
2. **Right-sizing**: Start with min instances = 0, scale based on actual load
3. **Storage lifecycle**: Move old files to Coldline/Archive storage classes
4. **Committed use**: Purchase 1-year commits for predictable workloads
5. **Budget alerts**: Set up billing alerts at 50%, 80%, 100% thresholds

## Security Recommendations
1. **VPC**: Run Cloud Run in VPC with private Cloud SQL connection
2. **IAM**: Use service accounts with least-privilege principles
3. **Identity Platform**: Built-in GDPR compliance features
4. **Encryption**: Enable customer-managed encryption keys (CMEK)
5. **Audit logs**: Enable Cloud Audit Logs for compliance tracking
6. **WAF**: Use Cloud Armor for DDoS protection and rate limiting

## Deployment Strategy
1. **CI/CD Pipeline**:
   - Cloud Build for automated builds on git push
   - Separate dev/staging/prod environments
   - Blue-green deployments with traffic splitting
   
2. **Infrastructure as Code**:
   - Terraform or Cloud Deployment Manager
   - Version control all infrastructure configs

3. **Monitoring**:
   - Cloud Monitoring for metrics and alerts
   - Cloud Logging for centralized logs
   - Error Reporting for exception tracking

## GDPR Compliance
- Data residency: Deploy in EU regions (europe-west1)
- Identity Platform: Built-in consent management
- Cloud DLP: Automatic PII detection and redaction
- Audit logs: 400-day retention for compliance

**Estimated Monthly Cost**: $500-2000 for 100k MAU (varies with actual usage patterns)
"""
        return True, demo_response, None, False
    
    if not model:
        return False, None, "Gemini API is not configured. Please check your API key.", False

    attempt = 0
    last_error = None
    while attempt <= max_retries:
        try:
            response = model.generate_content(prompt)
            if getattr(response, 'text', None):
                return True, response.text, None, False
            return False, None, "No response generated from Gemini API.", False
        except Exception as e:
            msg = str(e)
            last_error = msg
            # Detect rate limit/quota and retry a few times
            lower = msg.lower()
            is_rate = any(x in lower for x in ["429", "rate", "quota", "too many requests"])  # heuristic
            if is_rate and attempt < max_retries:
                # Exponential backoff: 1s, 2s, ...
                delay = 2 ** attempt
                time.sleep(delay)
                attempt += 1
                continue
            return False, None, f"Error generating architecture recommendation: {msg}", is_rate

    # Fallback (shouldn't reach here)
    return False, None, f"Error generating architecture recommendation: {last_error or 'Unknown error'}", False


def generate_architecture_recommendation(project_description):
    """
    Generate architecture recommendation using Gemini API.
    
    Args:
        project_description (str): User's project description
        
    Returns:
        tuple: (success: bool, response: str, error: str)
    """
    # Format the prompt with the project description
    prompt = ARCHITECTURE_PROMPT_TEMPLATE.format(project_description=project_description)
    success, text, error, _ = _generate_with_retry(prompt)
    return success, text, error

# Initialize Flask application
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def home():
    """Serve the main HTML template for the Cloud Architect AI interface."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate Google Cloud architecture recommendation based on project description.
    
    Expected JSON payload:
    {
        "prompt": "Project description string"
    }
    
    Returns:
        JSON response with architecture recommendation or error message
    """
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'error': 'Request must be JSON format'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'prompt' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Missing required field: prompt'
            }), 400
        
        project_description = data['prompt'].strip()
        
        # Validate input length and format
        if not project_description:
            return jsonify({
                'status': 'error',
                'error': 'Project description cannot be empty'
            }), 400
        
        if len(project_description) < 10:
            return jsonify({
                'status': 'error',
                'error': 'Project description must be at least 10 characters long'
            }), 400
        
        if len(project_description) > 5000:
            return jsonify({
                'status': 'error',
                'error': 'Project description must be less than 5000 characters'
            }), 400
        
        # Generate architecture recommendation
        success, response_text, error_message = generate_architecture_recommendation(project_description)
        
        # Log for debugging
        if not success:
            print(f"[ERROR] Generation failed: {error_message}")
        
        if success:
            return jsonify({
                'status': 'success',
                'response': response_text
            }), 200
        else:
            # Handle different types of API errors
            if "API key" in error_message:
                return jsonify({
                    'status': 'error',
                    'error': 'Service configuration error. Please try again later.'
                }), 500
            elif "quota" in error_message.lower() or "rate" in error_message.lower() or "429" in error_message:
                # Provide a Retry-After hint for clients
                response = jsonify({
                    'status': 'error',
                    'error': 'Service temporarily unavailable due to high demand. Please try again in a few minutes.'
                })
                return response, 429, {"Retry-After": "60"}
            else:
                return jsonify({
                    'status': 'error',
                    'error': 'Unable to generate architecture recommendation. Please try again.'
                }), 503
                
    except Exception as e:
        # Log the actual error for debugging (in production, use proper logging)
        print(f"Unexpected error in /generate endpoint: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

if __name__ == '__main__':
    # Development server configuration
    app.run(debug=True, host='0.0.0.0', port=8080)

# Basic health check endpoint (kept at end to avoid interfering with __main__ guard)
@app.route('/healthz')
def healthz():
    """Simple health check for uptime and configuration status."""
    return jsonify({
        'status': 'ok',
        'gemini_configured': model is not None,
        'demo_mode': DEMO_MODE
    }), 200