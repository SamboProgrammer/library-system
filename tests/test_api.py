import pytest
import json
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# ── Health ──────────────────────────────────────────────
def test_health_endpoint(client):
    r = client.get('/health')
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data['status'] == 'healthy'

def test_ready_endpoint(client):
    r = client.get('/ready')
    assert r.status_code == 200

# ── Books ────────────────────────────────────────────────
def test_list_books_empty(client):
    r = client.get('/api/books')
    assert r.status_code == 200
    assert json.loads(r.data) == []

def test_create_book(client):
    payload = {'isbn': '9781234567890', 'title': 'Clean Code', 'author': 'Robert Martin', 'genre': 'Tech', 'year': 2008}
    r = client.post('/api/books', json=payload)
    assert r.status_code == 201
    data = json.loads(r.data)
    assert data['title'] == 'Clean Code'
    assert data['available'] == 1

def test_create_book_duplicate_isbn(client):
    payload = {'isbn': '9781234567890', 'title': 'Book A', 'author': 'Author A'}
    client.post('/api/books', json=payload)
    r = client.post('/api/books', json=payload)
    assert r.status_code == 409

def test_create_book_missing_fields(client):
    r = client.post('/api/books', json={'title': 'No ISBN'})
    assert r.status_code == 400

def test_get_book(client):
    client.post('/api/books', json={'isbn': '000', 'title': 'T', 'author': 'A'})
    r = client.get('/api/books/1')
    assert r.status_code == 200

def test_update_book(client):
    client.post('/api/books', json={'isbn': '001', 'title': 'Old Title', 'author': 'A'})
    r = client.put('/api/books/1', json={'title': 'New Title'})
    assert r.status_code == 200
    assert json.loads(r.data)['title'] == 'New Title'

def test_delete_book(client):
    client.post('/api/books', json={'isbn': '002', 'title': 'To Delete', 'author': 'A'})
    r = client.delete('/api/books/1')
    assert r.status_code == 200
    assert client.get('/api/books/1').status_code == 404

def test_search_books(client):
    client.post('/api/books', json={'isbn': '003', 'title': 'Python Tricks', 'author': 'Dan Bader'})
    r = client.get('/api/books?q=python')
    assert r.status_code == 200
    assert len(json.loads(r.data)) == 1

# ── Members ──────────────────────────────────────────────
def test_create_member(client):
    r = client.post('/api/members', json={'name': 'Alice', 'email': 'alice@test.com'})
    assert r.status_code == 201
    data = json.loads(r.data)
    assert data['name'] == 'Alice'
    assert data['active'] == True

def test_create_member_duplicate_email(client):
    client.post('/api/members', json={'name': 'Alice', 'email': 'a@test.com'})
    r = client.post('/api/members', json={'name': 'Alice2', 'email': 'a@test.com'})
    assert r.status_code == 409

# ── Loans ────────────────────────────────────────────────
def _setup_book_member(client):
    client.post('/api/books', json={'isbn': '999', 'title': 'Book', 'author': 'Auth', 'copies': 1})
    client.post('/api/members', json={'name': 'Bob', 'email': 'bob@test.com'})

def test_create_loan(client):
    _setup_book_member(client)
    r = client.post('/api/loans', json={'book_id': 1, 'member_id': 1})
    assert r.status_code == 201
    data = json.loads(r.data)
    assert data['status'] == 'active'

def test_loan_reduces_availability(client):
    _setup_book_member(client)
    client.post('/api/loans', json={'book_id': 1, 'member_id': 1})
    r = client.get('/api/books/1')
    assert json.loads(r.data)['available'] == 0

def test_loan_no_copies_available(client):
    _setup_book_member(client)
    client.post('/api/loans', json={'book_id': 1, 'member_id': 1})
    r = client.post('/api/loans', json={'book_id': 1, 'member_id': 1})
    assert r.status_code == 409

def test_return_loan(client):
    _setup_book_member(client)
    client.post('/api/loans', json={'book_id': 1, 'member_id': 1})
    r = client.post('/api/loans/1/return')
    assert r.status_code == 200
    assert json.loads(r.data)['status'] == 'returned'

def test_return_restores_availability(client):
    _setup_book_member(client)
    client.post('/api/loans', json={'book_id': 1, 'member_id': 1})
    client.post('/api/loans/1/return')
    r = client.get('/api/books/1')
    assert json.loads(r.data)['available'] == 1
