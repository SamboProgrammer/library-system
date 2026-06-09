import json

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
