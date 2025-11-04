# Deployment Guide

This guide covers different deployment options for Cloud Architect AI.

## Google Cloud Run (Recommended)

Cloud Run is the recommended deployment platform as it provides:
- Automatic scaling from 0 to 1000+ instances
- Pay-per-request pricing
- HTTPS termination
- Global load balancing

### Prerequisites

1. Google Cloud Project with billing enabled
2. Cloud Run API enabled
3. Container Registry or Artifact Registry enabled
4. Google Cloud SDK installed and configured

### Automated Deployment with Cloud Build

1. **Setup Cloud Build trigger**:
   ```bash
   gcloud builds triggers create github \
     --repo-name=cloud-architect-ai \
     --repo-owner=YOUR_GITHUB_USERNAME \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. **Manual build and deploy**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

### Manual Deployment

1. **Build and push container**:
   ```bash
   # Set your project ID
   export PROJECT_ID=your-project-id
   
   # Build the image
   docker build -t gcr.io/$PROJECT_ID/cloud-architect-ai .
   
   # Push to Container Registry
   docker push gcr.io/$PROJECT_ID/cloud-architect-ai
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy cloud-architect-ai \
     --image gcr.io/$PROJECT_ID/cloud-architect-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 512Mi \
     --cpu 1 \
     --max-instances 10 \
     --set-env-vars GEMINI_API_KEY=your_gemini_api_key
   ```

3. **Configure custom domain** (optional):
   ```bash
   gcloud run domain-mappings create \
     --service cloud-architect-ai \
     --domain your-domain.com \
     --region us-central1
   ```

## Docker Deployment

### Local Docker

1. **Build the image**:
   ```bash
   docker build -t cloud-architect-ai .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8080:8080 \
     -e GEMINI_API_KEY=your_api_key \
     cloud-architect-ai
   ```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  cloud-architect-ai:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Other Cloud Platforms

### AWS App Runner

1. **Create apprunner.yaml**:
   ```yaml
   version: 1.0
   runtime: docker
   build:
     commands:
       build:
         - echo "No build commands"
   run:
     runtime-version: latest
     command: gunicorn --bind 0.0.0.0:8080 --workers 2 app:app
     network:
       port: 8080
       env: PORT
     env:
       - name: GEMINI_API_KEY
         value: your_api_key_here
   ```

2. **Deploy using AWS CLI**:
   ```bash
   aws apprunner create-service \
     --service-name cloud-architect-ai \
     --source-configuration '{
       "ImageRepository": {
         "ImageIdentifier": "your-ecr-repo/cloud-architect-ai:latest",
         "ImageConfiguration": {
           "Port": "8080"
         },
         "ImageRepositoryType": "ECR"
       },
       "AutoDeploymentsEnabled": true
     }'
   ```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name cloud-architect-ai \
  --image your-registry/cloud-architect-ai:latest \
  --dns-name-label cloud-architect-ai \
  --ports 8080 \
  --environment-variables GEMINI_API_KEY=your_api_key
```

## Environment Configuration

### Production Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `FLASK_ENV` | Flask environment | `production` |
| `SECRET_KEY` | Flask secret key | `your-secret-key` |

### Security Best Practices

1. **Use Secret Manager** (Google Cloud):
   ```bash
   # Store API key in Secret Manager
   echo "your_api_key" | gcloud secrets create gemini-api-key --data-file=-
   
   # Deploy with secret
   gcloud run deploy cloud-architect-ai \
     --image gcr.io/$PROJECT_ID/cloud-architect-ai \
     --set-secrets GEMINI_API_KEY=gemini-api-key:latest
   ```

2. **Use IAM for authentication**:
   ```bash
   # Remove public access
   gcloud run services remove-iam-policy-binding cloud-architect-ai \
     --member="allUsers" \
     --role="roles/run.invoker"
   
   # Add specific users
   gcloud run services add-iam-policy-binding cloud-architect-ai \
     --member="user:user@example.com" \
     --role="roles/run.invoker"
   ```

## Monitoring and Logging

### Google Cloud Monitoring

1. **Enable monitoring**:
   ```bash
   gcloud services enable monitoring.googleapis.com
   ```

2. **Create uptime check**:
   ```bash
   gcloud alpha monitoring uptime create \
     --display-name="Cloud Architect AI" \
     --http-check-path="/" \
     --hostname="your-service-url"
   ```

### Logging

Logs are automatically collected by Cloud Run. View them with:
```bash
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=cloud-architect-ai"
```

## Scaling Configuration

### Cloud Run Scaling

```bash
gcloud run services update cloud-architect-ai \
  --min-instances 1 \
  --max-instances 100 \
  --concurrency 80 \
  --cpu 2 \
  --memory 1Gi
```

### Performance Tuning

1. **Optimize container startup**:
   - Use multi-stage builds
   - Minimize image size
   - Use Python wheels

2. **Configure Gunicorn**:
   ```bash
   # In Dockerfile CMD
   gunicorn --bind 0.0.0.0:8080 \
     --workers 2 \
     --threads 4 \
     --timeout 120 \
     --keep-alive 2 \
     --max-requests 1000 \
     --max-requests-jitter 100 \
     app:app
   ```

## Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check logs: `gcloud logs read`
   - Verify environment variables
   - Test locally with Docker

2. **API key errors**:
   - Verify GEMINI_API_KEY is set
   - Check API key permissions
   - Ensure billing is enabled

3. **Memory issues**:
   - Increase memory allocation
   - Monitor memory usage
   - Optimize application code

### Health Checks

Add a health check endpoint to your application:
```python
@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

Configure health check in Cloud Run:
```bash
gcloud run services update cloud-architect-ai \
  --health-check-path="/health"
```