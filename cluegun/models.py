import transaction

from zope.interface import Interface
from zope.interface import implements

from datetime import datetime
from persistent import Persistent

from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated

from repoze.folder import Folder

class IPasteBin(Interface):
    pass

class PasteBin(Folder):
    implements(IPasteBin)
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, Authenticated, 'manage') ]

    current_id = -1

    def add_paste(self, paste):
        newid = self.current_id + 1
        self.current_id = newid
        pasteid = str(newid)
        self[pasteid] = paste
        return pasteid

class IPasteEntry(Interface):
    pass

class PasteEntry(Persistent):
    implements(IPasteEntry)
    def __init__(self, author_name, paste, language):
        self.author_name = author_name
        self.paste = paste
        self.language = language
        self.date = datetime.now()
        
def appmaker(root, transaction=transaction):
    if not root.has_key('cluegun.pastebin'):
        root['cluegun.pastebin'] = PasteBin()
        transaction.commit()
    return root['cluegun.pastebin']

