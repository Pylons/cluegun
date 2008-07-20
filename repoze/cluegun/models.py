from datetime import datetime
from persistent.mapping import PersistentMapping
from persistent import Persistent
from ZODB.DB import DB
from ZODB.FileStorage.FileStorage import FileStorage

from zope.interface import Interface
from zope.interface import implements
from zope.location.interfaces import ILocation

class IPasteBin(Interface):
    pass

class PasteBin(PersistentMapping):
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

class PasteEntry(Persistent):
    implements(IPasteEntry)

    def __init__(self, author_name, paste, language):
        self.author_name = author_name
        self.paste = paste
        self.language = language
        self.date = datetime.now()

class PersistentRootFinder:
    db = None
    def __init__(self, db_file):
        self.db_file = db_file

    def add_closer(self, environ, conn):
        class Closer:
            def __init__(self, conn):
                self.conn = conn
            def __del__(self):
                self.conn.close()
        closer = Closer(conn)
        environ['cluebin.closer'] = closer

    def __call__(self, environ):
        if self.db is None:
            storage = FileStorage(self.db_file)
            db = DB(storage)
            self.db = db
        conn = self.db.open()
        root = conn.root()
        if not root.has_key('cluegun.pastebin'):
            root['cluegun.pastebin'] = PasteBin()
        return root['cluegun.pastebin']
    
def NonPersistentRootFinder(db_path):
    bin = PasteBin()
    def get_root(environ):
        return bin
    return get_root

            
        
        
