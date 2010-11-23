import unittest

from pyramid.testing import DummyModel

class TestPasteBin(unittest.TestCase):
    def _makeOne(self, *arg, **kw):
        from cluegun.models import PasteBin
        return PasteBin(*arg, **kw)

    def test_add_paste(self):
        pastebin = self._makeOne()
        entry = DummyModel()
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
        
