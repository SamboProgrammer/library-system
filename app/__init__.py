from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, Histogram, generate_latest
import os

db = SQLAlchemy()

REQUEST_COUNT = Counter('library_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('library_request_duration_seconds', 'Request latency', ['endpoint'])
BOOK_OPERATIONS = Counter('library_book_operations_total', 'Book operations', ['operation'])

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///library.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    db.init_app(app)

    from app.routes.books import books_bp
    from app.routes.members import members_bp
    from app.routes.loans import loans_bp
    from app.routes.health import health_bp

    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(members_bp, url_prefix='/api/members')
    app.register_blueprint(loans_bp, url_prefix='/api/loans')
    app.register_blueprint(health_bp)

    with app.app_context():
        db.create_all()

    return app
