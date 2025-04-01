from datetime import datetime, timedelta
from functools import wraps

from flask import session, redirect, url_for, request


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_bp.login', next=request.url))

        last_activity = session.get('last_activity')
        if last_activity:
            last_active = datetime.fromisoformat(last_activity)
            if (datetime.now() - last_active) > timedelta(hours=1):
                session.clear()
                return redirect(url_for('auth_bp.login'))

        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)

    return decorated_function
