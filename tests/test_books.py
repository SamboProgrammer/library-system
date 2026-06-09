import json

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
