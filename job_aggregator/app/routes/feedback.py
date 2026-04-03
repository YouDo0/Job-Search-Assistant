from flask import Blueprint, redirect, jsonify, request
from ..models import Job, Feedback
from .. import db

bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@bp.route('/record', methods=['GET'])
def record():
    job_id = request.args.get('job_id')
    status = request.args.get('status')

    if not job_id or not status:
        return jsonify({'error': 'Missing job_id or status'}), 400

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    Feedback.query.filter_by(job_id=job_id).delete()

    feedback = Feedback(job_id=job_id, status=status)
    db.session.add(feedback)

    if status == 'not_interested':
        job.is_active = False

    db.session.commit()

    return jsonify({'success': True, 'status': status})
