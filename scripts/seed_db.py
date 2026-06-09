#!/usr/bin/env python3
"""Seed the database with sample data for development/demo."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.models import Book, Member, Loan
from datetime import datetime, timedelta

BOOKS = [
    {"isbn": "9780132350884", "title": "Clean Code", "author": "Robert C. Martin", "genre": "Engineering", "year": 2008, "copies": 3},
    {"isbn": "9780201633610", "title": "Design Patterns", "author": "Gang of Four", "genre": "Engineering", "year": 1994, "copies": 2},
    {"isbn": "9780596517748", "title": "JavaScript: The Good Parts", "author": "Douglas Crockford", "genre": "Programming", "year": 2008, "copies": 4},
    {"isbn": "9781491950357", "title": "Python Cookbook", "author": "David Beazley", "genre": "Programming", "year": 2013, "copies": 2},
    {"isbn": "9780134685991", "title": "Effective Java", "author": "Joshua Bloch", "genre": "Programming", "year": 2018, "copies": 3},
    {"isbn": "9781617294945", "title": "Docker in Action", "author": "Jeff Nickoloff", "genre": "DevOps", "year": 2019, "copies": 2},
    {"isbn": "9780596009205", "title": "Learning Python", "author": "Mark Lutz", "genre": "Programming", "year": 2013, "copies": 5},
    {"isbn": "9780321751041", "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "genre": "Engineering", "year": 2019, "copies": 3},
]

MEMBERS = [
    {"name": "Alice Johnson", "email": "alice@library.com", "phone": "555-0101", "membership_type": "premium"},
    {"name": "Bob Smith", "email": "bob@library.com", "phone": "555-0102", "membership_type": "standard"},
    {"name": "Carol White", "email": "carol@library.com", "phone": "555-0103", "membership_type": "standard"},
    {"name": "David Brown", "email": "david@library.com", "phone": "555-0104", "membership_type": "premium"},
    {"name": "Eve Davis", "email": "eve@library.com", "phone": "555-0105", "membership_type": "standard"},
]

def seed():
    app = create_app()
    with app.app_context():
        print("Clearing existing data...")
        Loan.query.delete()
        Book.query.delete()
        Member.query.delete()
        db.session.commit()

        print("Seeding books...")
        books = []
        for b in BOOKS:
            book = Book(**b, available=b['copies'])
            db.session.add(book)
            books.append(book)
        db.session.commit()

        print("Seeding members...")
        members = []
        for m in MEMBERS:
            member = Member(**m)
            db.session.add(member)
            members.append(member)
        db.session.commit()

        print("Seeding loans...")
        loan1 = Loan(book_id=books[0].id, member_id=members[0].id,
                     due_date=datetime.utcnow() + timedelta(days=14))
        books[0].available -= 1

        loan2 = Loan(book_id=books[2].id, member_id=members[1].id,
                     due_date=datetime.utcnow() - timedelta(days=2),
                     status='overdue')
        books[2].available -= 1

        loan3 = Loan(book_id=books[1].id, member_id=members[2].id,
                     due_date=datetime.utcnow() - timedelta(days=5),
                     returned_at=datetime.utcnow() - timedelta(days=1),
                     status='returned')

        for loan in [loan1, loan2, loan3]:
            db.session.add(loan)
        db.session.commit()

        print(f"✅ Seeded {len(BOOKS)} books, {len(MEMBERS)} members, 3 loans")

if __name__ == '__main__':
    seed()
