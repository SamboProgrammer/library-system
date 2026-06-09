from flask import Blueprint, request, jsonify
from app import db, BOOK_OPERATIONS
from app.models.models import Book
from flask_jwt_extended import jwt_required

books_bp = Blueprint('books', __name__)

# Fetch all books with optional search filtering (Protected Route)
@books_bp.route('', methods=['GET'])
@jwt_required()
def list_books():
    q = request.args.get('q', '')
    genre = request.args.get('genre', '')
    query = Book.query
    if q:
        query = query.filter(Book.title.ilike(f'%{q}%') | Book.author.ilike(f'%{q}%'))
    if genre:
        query = query.filter(Book.genre == genre)
    books = query.all()
    return jsonify([b.to_dict() for b in books])

# Get a single book record by ID
@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

# Add a new book to the library catalog
@books_bp.route('', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get('isbn') or not data.get('title') or not data.get('author'):
        return jsonify({'error': 'isbn, title, author required'}), 400
    if Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': 'ISBN already exists'}), 409
    book = Book(
        isbn=data['isbn'], title=data['title'], author=data['author'],
        genre=data.get('genre'), year=data.get('year'),
        copies=data.get('copies', 1), available=data.get('copies', 1)
    )
    db.session.add(book)
    db.session.commit()
    BOOK_OPERATIONS.labels(operation='create').inc()
    return jsonify(book.to_dict()), 201

# Modify an existing book record
@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    for field in ['title', 'author', 'genre', 'year', 'copies']:
        if field in data:
            setattr(book, field, data[field])
    db.session.commit()
    BOOK_OPERATIONS.labels(operation='update').inc()
    return jsonify(book.to_dict())

# Remove a book from the catalog
@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    BOOK_OPERATIONS.labels(operation='delete').inc()
    return jsonify({'message': 'deleted'}), 200
