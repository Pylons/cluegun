import datetime

class Paste(object):
    author_name = None
    language = None
    paste = None
    date = None
    pasteid = None

    def __str__(self):
        return '<%s pasteid=%s>' % (self.__class__.__name__, self.pasteid)

    __repr__ = __str__


class PasteDataStore(object):
    """An in-memory implementation of a datastore, no persistence."""

    def __init__(self):
        self.pastes = {}

    def get_paste(self, pasteid):
        return self.pastes.get(int(pasteid))

    def get_pastes(self):
        return self.pastes.values()

    def gen_paste(self):
        return Paste()

    def save_paste(self, p):
        p.pasteid = len(self.pastes)+1
        self.pastes[p.pasteid] = p


class PasteManager(object):
    """Component for managing projects.

      >>> pmanager = PasteManager()
      >>> pmanager.get_pastes()
      []

      >>> p = pmanager.save_paste('foo', 'abc', 'def')
      >>> p
      <Paste pasteid=1>
      >>> pmanager.get_paste(1)
      <Paste pasteid=1>
      >>> pmanager.get_pastes()
      [<Paste pasteid=1>]

    """

    def __init__(self, datastore=None):
        if datastore is None:
            datastore = PasteDataStore()
        self.datastore = datastore

    def get_paste(self, pasteid):
        return self.datastore.get_paste(pasteid)

    def get_pastes(self):
        return self.datastore.get_pastes()

    def save_paste(self, author_name, paste_text, language):
        p = self.datastore.gen_paste()
        p.author_name = author_name
        p.paste = paste_text
        p.language = language
        p.date = datetime.datetime.now()
        self.datastore.save_paste(p)
        return p
