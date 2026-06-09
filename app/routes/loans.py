from flask import Blueprint, request, jsonify, current_app # 🛠️ បានបន្ថែម current_app សម្រាប់ហៅប្រើប្រាស់ Logger
from app import db
from app.models.models import Book, Member, Loan
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import jwt_required

loans_bp = Blueprint('loans', __name__)

# Fetch all library loans (Protected route)
@loans_bp.route('', methods=['GET'])
@jwt_required()
def list_loans():
    status = request.args.get('status', '')
    query = Loan.query
    if status:
        query = query.filter(Loan.status == status)
    loans = query.order_by(Loan.loaned_at.desc()).all()
    return jsonify([l.to_dict() for l in loans])

# Create a new book loan record
@loans_bp.route('', methods=['POST'])
def create_loan():
    data = request.get_json()
    book = Book.query.get_or_404(data.get('book_id'))
    member = Member.query.get_or_404(data.get('member_id'))

    if book.available < 1:
        return jsonify({'error': 'No copies available'}), 409
    if not member.active:
        return jsonify({'error': 'Member account inactive'}), 403

    due_days = 14 if member.membership_type == 'standard' else 30
    loan = Loan(
        book_id=book.id, member_id=member.id,
        due_date=datetime.now(timezone.utc) + timedelta(days=due_days)
    )
    book.available -= 1
    db.session.add(loan)
    db.session.commit()

    # 🛠️ ជំហានទី ២០ — បន្ថែមការកត់ត្រា Log ពេលបង្កើតការខ្ចីសៀវភៅជោគជ័យ
    current_app.logger.info(f"Loan created successfully — Member ID: {member.id} borrowed Book ID: {book.id}")

    return jsonify(loan.to_dict()), 201

# Process a book return request
@loans_bp.route('/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.status == 'returned':
        return jsonify({'error': 'Already returned'}), 409
    
    loan.returned_at = datetime.now(timezone.utc)
    loan.status = 'returned'
    loan.book.available += 1
    db.session.commit()

    # 🛠️ ជំហានទី ២០ — បន្ថែមការកត់ត្រា Log ពេលសមាជិកយកសៀវភៅមកសងវិញជោគជ័យ
    current_app.logger.info(f"Book returned successfully — Loan ID: {loan.id} updated to returned status")

    return jsonify(loan.to_dict())

# Scan and retrieve all past-due loans
@loans_bp.route('/overdue', methods=['GET'])
def overdue_loans():
    now = datetime.now(timezone.utc)
    loans = Loan.query.filter(
        Loan.status == 'active', Loan.due_date < now
    ).all()
    for loan in loans:
        loan.status = 'overdue'
    db.session.commit()
    return jsonify([l.to_dict() for l in loans])
