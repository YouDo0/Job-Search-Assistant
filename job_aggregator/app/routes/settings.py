from flask import Blueprint, render_template, request, jsonify
from ..models import UserPreference
import json

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
def settings_page():
    return render_template('settings.html')

@bp.route('/api/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        data = request.get_json()
        for key, value in data.items():
            UserPreference.set(key, value)
        return jsonify({'success': True})

    prefs = UserPreference.query.all()
    return jsonify({p.key: json.loads(p.value) if p.value else None for p in prefs})
