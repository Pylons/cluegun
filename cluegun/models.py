import transaction

from zope.interface import Interface
from zope.interface import implementer

from datetime import datetime
from persistent import Persistent

from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated

from repoze.folder import Folder

class IPasteBin(Interface):
    pass

@implementer(IPasteBin)
class PasteBin(Folder):
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

@implementer(IPasteEntry)
class PasteEntry(Persistent):
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

