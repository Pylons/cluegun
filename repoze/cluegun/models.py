from zope.interface import Interface
from zope.interface import implements

class IPasteBin(Interface):
    pass

class PasteBin(object):
    implements(IPasteBin)

def get_root(environ):
    root = PasteBin()
    return root


