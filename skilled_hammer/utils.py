import hashlib
import hmac


def valid_github_http_headers(request):
    if 'HTTP_X_GITHUB_DELIVERY' not in request.headers:
        return False

    if 'HTTP_USER_AGENT' not in request.headers or request.headers['HTTP_USER_AGENT'][:16] != 'GitHub-Hookshot/':
        return False

    if 'HTTP_X_GITHUB_EVENT' not in request.headers or request.headers['HTTP_X_GITHUB_EVENT'] != 'push':
        return False

    if 'HTTP_X_GITHUB_SIGNATURE' not in request.headers:
        return False
    else:
        from main import app
        hmac_digest = hmac.new(app.config['HAMMER_SECRET'], request.data, hashlib.sha1).hexdigest()
        if hmac_digest != request.headers['HTTP_X_GITHUB_SIGNATURE']:
            return False

    return True
