import pytest
from app import create_app, db
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key-12345'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    # Automatically injects a valid authorization token into the mock client
    with app.app_context():
        token = create_access_token(identity="test_admin")
    
    test_client = app.test_client()
    # Force the client to send the header on every request automatically
    test_client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return test_client
