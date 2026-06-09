from flask import Blueprint, request, jsonify
from app import db
from app.models.models import Book, Member, Loan
from datetime import datetime, timedelta

loans_bp = Blueprint('loans', __name__)

@loans_bp.route('', methods=['GET'])
def list_loans():
    status = request.args.get('status', '')
    query = Loan.query
    if status:
        query = query.filter(Loan.status == status)
    loans = query.order_by(Loan.loaned_at.desc()).all()
    return jsonify([l.to_dict() for l in loans])

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
        due_date=datetime.utcnow() + timedelta(days=due_days)
    )
    book.available -= 1
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201

@loans_bp.route('/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.status == 'returned':
        return jsonify({'error': 'Already returned'}), 409
    loan.returned_at = datetime.utcnow()
    loan.status = 'returned'
    loan.book.available += 1
    db.session.commit()
    return jsonify(loan.to_dict())

@loans_bp.route('/overdue', methods=['GET'])
def overdue_loans():
    now = datetime.utcnow()
    loans = Loan.query.filter(
        Loan.status == 'active', Loan.due_date < now
    ).all()
    for loan in loans:
        loan.status = 'overdue'
    db.session.commit()
    return jsonify([l.to_dict() for l in loans])
