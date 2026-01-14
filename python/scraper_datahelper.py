try:
    from urlparse import parse_qsl
except ImportError:  # py2 / py3
    from urllib.parse import parse_qsl

def get_params(argv):
    """Get addon params from the plugin path querystring"""
    result = {'handle': int(argv[0])}
    if len(argv) < 2 or not argv[1]:
        return result

    result.update(parse_qsl(argv[1].lstrip('?')))
    return result
