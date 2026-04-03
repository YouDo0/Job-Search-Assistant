from flask import Blueprint, render_template, jsonify, request
from .. import db
from ..models import Job, Feedback

bp = Blueprint('jobs', __name__, url_prefix='/')

@bp.route('/')
def index():
    source = request.args.get('source')
    status = request.args.get('status')

    query = Job.query.filter_by(is_active=True)

    if source:
        query = query.filter_by(source=source)

    jobs = query.order_by(Job.scraped_at.desc()).limit(50).all()

    if status:
        if status == 'applied':
            jobs = [j for j in jobs if j.feedback and j.feedback[0].status == 'applied']
        elif status == 'not_interested':
            jobs = [j for j in jobs if j.feedback and j.feedback[0].status == 'not_interested']
        elif status == 'undecided':
            jobs = [j for j in jobs if not j.feedback]

    return render_template('index.html', jobs=jobs)

@bp.route('/api/jobs')
def api_jobs():
    jobs = Job.query.filter_by(is_active=True).order_by(Job.scraped_at.desc()).limit(50).all()
    return jsonify([j.to_dict() for j in jobs])
