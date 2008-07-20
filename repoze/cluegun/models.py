from datetime import datetime

from zope.interface import Interface
from zope.interface import implements
from zope.location.interfaces import ILocation

class IPasteBin(Interface):
    pass

class PasteBin(dict):
    implements(IPasteBin, ILocation)

    current_id = -1

    def add_paste(self, paste):
        newid = self.current_id + 1
        self.current_id = newid
        pasteid = str(newid)
        self[pasteid] = paste
        return pasteid

class IPasteEntry(Interface):
    pass

class PasteEntry(object):
    implements(IPasteEntry)

    def __init__(self, author_name, paste, language):
        self.author_name = author_name
        self.paste = paste
        self.language = language
        self.date = datetime.now()

root = PasteBin()

def get_root(environ):
    return root

