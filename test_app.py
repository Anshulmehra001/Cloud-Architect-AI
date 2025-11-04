# Cloud Architect AI Test Suite
import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, generate_architecture_recommendation

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def mock_gemini_model():
    """Mock the Gemini model for testing without real API calls."""
    mock_response = MagicMock()
    mock_response.text = """
# Google Cloud Architecture Recommendation

## Recommended Services
- **Compute Engine**: For scalable virtual machines
- **Cloud Storage**: For object storage needs
- **Cloud SQL**: For managed relational database

## Architecture Overview
Your application would benefit from a microservices architecture using:
1. Load Balancer for traffic distribution
2. Compute Engine instances for application hosting
3. Cloud SQL for data persistence
4. Cloud Storage for static assets

## Security Recommendations
- Use IAM for access control
- Enable VPC for network isolation
- Implement Cloud Armor for DDoS protection
"""
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    return mock_model

@pytest.fixture
def sample_project_description():
    """Sample project description for testing."""
    return "A web application for managing customer orders with user authentication, payment processing, and inventory management."

# Test Cases

def test_home_page_loads(client):
    """Test that the main route returns 200 status and serves the HTML template."""
    response = client.get('/')
    
    assert response.status_code == 200
    assert response.content_type.startswith('text/html')
    # Verify that the response contains expected HTML elements
    assert b'Cloud Architect AI' in response.data or b'textarea' in response.data

@patch('app.model')
def test_generate_endpoint_mocked(mock_model, client, mock_gemini_model, sample_project_description):
    """Test the generate endpoint with mocked Gemini API responses."""
    # Set up the mock
    mock_model.return_value = mock_gemini_model
    mock_model.generate_content = mock_gemini_model.generate_content
    
    # Test successful generation
    response = client.post('/generate', 
                          json={'prompt': sample_project_description},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'response' in data
    assert 'Google Cloud Architecture' in data['response']

def test_generate_endpoint_validation_errors(client):
    """Test input validation for the generate endpoint."""
    # Test missing JSON content type
    response = client.post('/generate', data='not json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'JSON format' in data['error']
    
    # Test missing prompt field
    response = client.post('/generate', 
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Missing required field' in data['error']
    
    # Test empty prompt
    response = client.post('/generate', 
                          json={'prompt': ''},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'cannot be empty' in data['error']
    
    # Test prompt too short
    response = client.post('/generate', 
                          json={'prompt': 'short'},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'at least 10 characters' in data['error']
    
    # Test prompt too long
    long_prompt = 'x' * 5001
    response = client.post('/generate', 
                          json={'prompt': long_prompt},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'less than 5000 characters' in data['error']

@patch('app.model', None)
def test_generate_endpoint_no_api_key(client, sample_project_description):
    """Test error handling when Gemini API is not configured."""
    response = client.post('/generate', 
                          json={'prompt': sample_project_description},
                          content_type='application/json')
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'configuration error' in data['error']

@patch('app.model')
def test_generate_endpoint_api_error(mock_model, client, sample_project_description):
    """Test error handling when Gemini API throws an exception."""
    # Mock API to raise an exception
    mock_model.generate_content.side_effect = Exception("API Error")
    
    response = client.post('/generate', 
                          json={'prompt': sample_project_description},
                          content_type='application/json')
    
    assert response.status_code == 503
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Unable to generate' in data['error']

def test_healthz_endpoint(client):
    """Health endpoint should return 200 and include gemini_configured flag."""
    response = client.get('/healthz')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'gemini_configured' in data

def test_generate_architecture_recommendation_success():
    """Test the generate_architecture_recommendation function with mocked model."""
    with patch('app.model') as mock_model:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = "Test architecture recommendation"
        mock_model.generate_content.return_value = mock_response
        
        success, response, error = generate_architecture_recommendation("Test project description")
        
        assert success is True
        assert response == "Test architecture recommendation"
        assert error is None

def test_generate_architecture_recommendation_no_model():
    """Test the generate_architecture_recommendation function when model is None."""
    with patch('app.model', None):
        success, response, error = generate_architecture_recommendation("Test project")
        
        assert success is False
        assert response is None
        assert "not configured" in error

def test_generate_architecture_recommendation_api_exception():
    """Test the generate_architecture_recommendation function when API throws exception."""
    with patch('app.model') as mock_model:
        mock_model.generate_content.side_effect = Exception("Test API error")
        
        success, response, error = generate_architecture_recommendation("Test project")
        
        assert success is False
        assert response is None
        assert "Error generating" in error