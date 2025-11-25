from flask import abort, request, session
import secrets

def get_ip_address() -> str:
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    

def get_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_hex(32)
        session['csrf_token'] = token
    return token


def setup_csrf(app):
    @app.before_request
    def csrf_protect():
        if app.config.get('TESTING') or not app.config.get('CSRF_PROTECTION'):
            return None
        
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            header_token = request.headers.get('X-CSRF-Token')
            session_token = session.get('csrf_token')
            if not header_token or not session_token or header_token != session_token:
                abort(403, 'CSRF token is missing or is invalid.')
