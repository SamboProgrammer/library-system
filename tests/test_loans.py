import json

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
