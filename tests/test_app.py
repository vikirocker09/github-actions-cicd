import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200

def test_get_items(client):
    response = client.get('/api/items')
    assert response.status_code == 200

def test_add_item(client):
    response = client.post('/api/items', json={"name": "test item"})
    assert response.status_code == 201
