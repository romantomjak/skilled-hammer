def valid_github_http_headers(headers):
    if 'HTTP_X_GITHUB_DELIVERY' not in headers:
        return False

    if 'HTTP_USER_AGENT' not in headers or headers['HTTP_USER_AGENT'][:16] != 'GitHub-Hookshot/':
        return False

    if 'HTTP_X_GITHUB_EVENT' not in headers or headers['HTTP_X_GITHUB_EVENT'] != 'push':
        return False

    if 'HTTP_X_GITHUB_SIGNATURE' not in headers:
        return False
    else:
        # TODO: verify signature
        pass

    return True
