import pytest
from app import app, db, Category

@pytest.fixture
def client():
    # Set up temporary test configurations
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # In-memory database isolated from production
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# Test POST (Positive & Negative) [cite: 22, 24]
def test_create_category(client):
    # Positive Case [cite: 22]
    response = client.post('/api/v1/categories', json={"name": "Work", "description": "Office tasks"})
    assert response.status_code == 201
    assert response.get_json()['name'] == "Work"

    # Negative Case: Missing name parameter [cite: 22]
    bad_response = client.post('/api/v1/categories', json={"description": "No name here"})
    assert bad_response.status_code == 400

    # Negative Case: Duplicate insertion name [cite: 22]
    dup_response = client.post('/api/v1/categories', json={"name": "Work"})
    assert dup_response.status_code == 409

# Test GET All [cite: 24]
def test_get_all_categories(client):
    client.post('/api/v1/categories', json={"name": "Personal"})
    client.post('/api/v1/categories', json={"name": "Urgent"})
    
    response = client.get('/api/v1/categories')
    assert response.status_code == 200
    assert len(response.get_json()) == 2

# Test GET Single (Positive & Negative) [cite: 22, 24]
def test_get_single_category(client):
    # Setup base data
    res = client.post('/api/v1/categories', json={"name": "Health"})
    cat_id = res.get_json()['id']

    # Positive case [cite: 22]
    response = client.get(f'/api/v1/categories/{cat_id}')
    assert response.status_code == 200
    assert response.get_json()['name'] == "Health"

    # Negative case: Requesting invalid id [cite: 22]
    response_404 = client.get('/api/v1/categories/999')
    assert response_404.status_code == 404

# Test PUT Update (Positive & Negative) [cite: 22, 24]
def test_update_category(client):
    res = client.post('/api/v1/categories', json={"name": "School", "description": "Homework"})
    cat_id = res.get_json()['id']

    # Positive case [cite: 22]
    response = client.put(f'/api/v1/categories/{cat_id}', json={"description": "University tasks"})
    assert response.status_code == 200
    assert response.get_json()['description'] == "University tasks"

    # Negative case: Bad JSON body [cite: 22]
    response_bad = client.put(f'/api/v1/categories/{cat_id}', data="Not JSON format")
    assert response_bad.status_code == 400

    # Negative case: 404 execution path [cite: 22]
    response_404 = client.put('/api/v1/categories/999', json={"name": "Ghost"})
    assert response_404.status_code == 404

# Test DELETE (Positive & Negative) [cite: 22, 24]
def test_delete_category(client):
    res = client.post('/api/v1/categories', json={"name": "Temp"})
    cat_id = res.get_json()['id']

    # Positive case [cite: 22]
    response = client.delete(f'/api/v1/categories/{cat_id}')
    assert response.status_code == 200

    # Negative case: Delete non-existing asset [cite: 22]
    response_404 = client.delete('/api/v1/categories/{cat_id}')
    assert response_404.status_code == 404
