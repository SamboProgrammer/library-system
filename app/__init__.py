from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, Histogram, generate_latest
from flask_jwt_extended import JWTManager
import os

# ១. ត្រូវបង្កើត db និង jwt នៅខាងលើគេបង្អស់ (មុនពេល Import Blueprint ណាមួយ)
db = SQLAlchemy()
jwt = JWTManager()

REQUEST_COUNT = Counter('library_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('library_request_duration_seconds', 'Request latency', ['endpoint'])
BOOK_OPERATIONS = Counter('library_book_operations_total', 'Book operations', ['operation'])

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///library.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me')

    # ២. ភ្ជាប់ db និង jwt ទៅកាន់ app មុនគេ
    db.init_app(app)
    jwt.init_app(app)

    # ៣. 🚨 យកការ Import Blueprints ទាំងអស់ (រួមទាំង auth_bp) មកដាក់ក្នុង create_app() វិញ
    # ការធ្វើបែបនេះហៅថា Local Import វាជួយបំបាត់បញ្ហាទាញយកកូដវិលជុំជាន់គ្នា (Circular Import)
    from app.routes.auth import auth_bp
    from app.routes.books import books_bp
    from app.routes.members import members_bp
    from app.routes.loans import loans_bp
    from app.routes.health import health_bp

    # ៤. ចុះឈ្មោះ (Register) គ្រប់ Blueprints ទាំងអស់ចូលទៅក្នុង app
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(members_bp, url_prefix='/api/members')
    app.register_blueprint(loans_bp, url_prefix='/api/loans')
    app.register_blueprint(health_bp)

    with app.app_context():
        db.create_all()

    return app
