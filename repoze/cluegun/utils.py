import logging
import os


def setup_logger():
    """Configure and return the initial cluebin logger.

      >>> setup_logger()
      <logging.Logger ...>
    """

    formatter = logging.Formatter('%(asctime)s %(levelname)-5.5s '
                                  '[%(name)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger('cluebin')
    logger.addHandler(handler)
    logger.setLevel(int(os.environ.get('cluebin.loglevel', logging.INFO)))

    return logger


def importattr(fullname):
    """Retrieve the attribute identified by *fullname* by importing
    appopriate modules and accessing the attribute.

      >>> importattr('sys')
      <module 'sys' ...>

      >>> importattr('os.path.join')
      <function join ...>

      >>> importattr('os.environ')
      {...}
    """

    left = fullname.split('.')
    if len(left) == 1:
        return __import__(fullname)

    attrname = left[-1]
    left = left[:-1]
    if len(left) == 1:
        importargs = left
    else:
        mname = left[-1]
        package = left[:-1][0]
        importargs = [package+'.'+mname, locals(), globals(), [package]]

    m = __import__(*importargs)
    f = getattr(m, attrname)
    return f


def url(request, s):
    """Generate an absolute url based on the web application root and appending
    *s*.

      >>> class Request(object):
      ...     def __init__(self, url, path_info=None):
      ...         self.url = url; self.path_info = path_info

      >>> url(Request('http://foo.com'), 'here')
      'http://foo.com/here'

      >>> url(Request('http://foo.com/myapp/'), 'somewhere/else')
      'http://foo.com/myapp/somewhere/else'
    """

    url = request.url
    if request.path_info:
        url = url[:-1*len(request.path_info)]
    if not url.endswith('/'):
        url += '/'
    return url + s
