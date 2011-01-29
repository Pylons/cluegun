import unittest

from pyramid import testing

class TestPasteBin(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from cluegun.models import PasteBin
        return PasteBin(*arg, **kw)

    def test_add_paste(self):
        pastebin = self._makeOne()
        entry = testing.DummyResource()
        pastebin.add_paste(entry)
        self.assertEqual(pastebin[0], entry)
        self.assertEqual(pastebin.current_id, 0)
        
class TestPasteEntry(unittest.TestCase):
    def _makeOne(self, author_name, paste, language):
        from cluegun.models import PasteEntry
        return PasteEntry(author_name, paste, language)

    def test_ctor(self):
        entry = self._makeOne('author_name', 'paste', 'language')
        self.assertEqual(entry.author_name, 'author_name')
        self.assertEqual(entry.paste, 'paste')
        self.assertEqual(entry.language, 'language')
        self.failUnless(entry.date)
        
class Test_appmaker(unittest.TestCase):
    def _callFUT(self, root, txn):
        from cluegun.models import appmaker
        return appmaker(root, txn)

    def test_already_exists(self):
        root = {'cluegun.pastebin':'abc'}
        txn = DummyTransaction()
        result = self._callFUT(root, txn)
        self.assertEqual(result, 'abc')
        self.failIf(txn.committed)

    def test_doesnt_exist(self):
        from cluegun.models import PasteBin
        root = {}
        txn = DummyTransaction()
        result = self._callFUT(root, txn)
        self.assertEqual(result.__class__, PasteBin)
        self.failUnless(txn.committed)
        
class DummyTransaction(object):
    committed = False
    def commit(self):
        self.committed = True
        
