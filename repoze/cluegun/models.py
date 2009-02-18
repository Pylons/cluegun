from datetime import datetime
from persistent.mapping import PersistentMapping
from persistent import Persistent

from zope.interface import Interface
from zope.interface import implements
from repoze.bfg.interfaces import ILocation

from repoze.bfg.security import Allow
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

class IPasteBin(Interface):
    pass

class PasteBin(PersistentMapping):
    implements(IPasteBin, ILocation)
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
        
def appmaker(root):
    if not root.has_key('cluegun.pastebin'):
        root['cluegun.pastebin'] = PasteBin()
        import transaction
        transaction.commit()
    return root['cluegun.pastebin']

def NonPersistentRootFinder(db_path):
    bin = PasteBin()
    def get_root(environ):
        return bin
    return get_root

            
        
        
