from flask import Blueprint, request, jsonify, current_app # បានបន្ថែម current_app សម្រាប់ហៅប្រើប្រាស់ Logger
from app import db
from app.models.models import Member
from flask_jwt_extended import jwt_required

members_bp = Blueprint('members', __name__)

# Fetch all active members (Protected route)
@members_bp.route('', methods=['GET'])
@jwt_required()
def list_members():
    members = Member.query.filter_by(active=True).all()
    return jsonify([m.to_dict() for m in members])

# Get a single member by ID
@members_bp.route('/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify(member.to_dict())

# Register a new member
@members_bp.route('', methods=['POST'])
def create_member():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'name, email required'}), 400
    if Member.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    member = Member(
        name=data['name'], email=data['email'],
        phone=data.get('phone'),
        membership_type=data.get('membership_type', 'standard')
    )
    db.session.add(member)
    db.session.commit()
    
    # 🛠️ ជំហានទី ២០ — កែប្រែដោយបន្ថែមការកត់ត្រាព័ត៌មាន (Log) ពេលចុះឈ្មោះសមាជិកជោគជ័យ
    current_app.logger.info(f"Member registered: {member.name} (Email: {member.email})")
    
    return jsonify(member.to_dict()), 201

# Update member details
@members_bp.route('/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    for field in ['name', 'phone', 'membership_type', 'active']:
        if field in data:
            setattr(member, field, data[field])
    db.session.commit()
    return jsonify(member.to_dict())

# Soft delete / Deactivate a member
@members_bp.route('/<int:member_id>', methods=['DELETE'])
def deactivate_member(member_id):
    member = Member.query.get_or_404(member_id)
    member.active = False
    db.session.commit()
    return jsonify({'message': 'deactivated'})
