from flask import Blueprint, jsonify, Response
from app import db
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {str(e)}'
    return jsonify({
        'status': 'healthy' if db_status == 'ok' else 'unhealthy',
        'timestamp': time.time(),
        'database': db_status,
        'version': '1.0.0'
    })

@health_bp.route('/ready')
def ready():
    return jsonify({'status': 'ready'})

@health_bp.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
