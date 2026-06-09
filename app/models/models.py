from app import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    year = db.Column(db.Integer)
    copies = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'isbn': self.isbn, 'title': self.title,
            'author': self.author, 'genre': self.genre, 'year': self.year,
            'copies': self.copies, 'available': self.available,
            'created_at': self.created_at.isoformat()
        }

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    membership_type = db.Column(db.String(20), default='standard')
    active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'email': self.email,
            'phone': self.phone, 'membership_type': self.membership_type,
            'active': self.active, 'joined_at': self.joined_at.isoformat()
        }

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    loaned_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, returned, overdue

    book = db.relationship('Book', backref='loans')
    member = db.relationship('Member', backref='loans')

    def to_dict(self):
        return {
            'id': self.id, 'book_id': self.book_id, 'member_id': self.member_id,
            'book_title': self.book.title if self.book else None,
            'member_name': self.member.name if self.member else None,
            'loaned_at': self.loaned_at.isoformat(),
            'due_date': self.due_date.isoformat(),
            'returned_at': self.returned_at.isoformat() if self.returned_at else None,
            'status': self.status
        }
