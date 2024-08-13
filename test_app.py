import pytest
import json
from flask import Flask
from app import app, client  # Adjust import based on your actual file structure

# Create a test client using Flask's test client
@pytest.fixture
def test_client():
    with app.test_client() as client:
        yield client

def test_index(test_client):
    """
    Test the index route for rendering the main chat interface.
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data  # Assuming your index.html has a DOCTYPE declaration

def test_post_chat(test_client):
    """
    Test the POST request for storing user messages.
    """
    response = test_client.post('/chat', 
                                data=json.dumps({"message": "Hello, how are you?"}),
                                content_type='application/json')
    assert response.status_code == 200

def test_get_chat(test_client, monkeypatch):
    """
    Test the GET request for streaming the AI response.
    """
    # Mock the client.chat.completions.create to return a controlled response
    def mock_create_response(model, messages, stream):
        class MockResponse:
            def __init__(self):
                self.choices = [MockChoice()]
        
        class MockChoice:
            def __init__(self):
                self.delta = {'content': 'Hello, how can I help you?'}
        
        return MockResponse()
    
    monkeypatch.setattr(client.chat, 'completions.create', mock_create_response)
    
    # Post a message to set the user message
    test_client.post('/chat', 
                     data=json.dumps({"message": "Hello"}),
                     content_type='application/json')
    
    # Get the streamed response
    response = test_client.get('/chat')
    
    assert response.status_code == 200
    assert b'data: Hello, how can I help you?' in response.data

def test_post_log(test_client):
    """
    Test the POST request for logging user queries, bot responses, and errors.
    """
    # Log a user query
    response = test_client.post('/log', 
                                data=json.dumps({"type": "user_query", "message": "Test query"}),
                                content_type='application/json')
    assert response.status_code == 200
    
    # Log a bot response
    response = test_client.post('/log', 
                                data=json.dumps({"type": "bot_response", "message": "Test response"}),
                                content_type='application/json')
    assert response.status_code == 200
    
    # Log an error
    response = test_client.post('/log', 
                                data=json.dumps({"type": "error", "message": "Test error"}),
                                content_type='application/json')
    assert response.status_code == 200
