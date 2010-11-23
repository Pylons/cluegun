import unittest

from pyramid import testing

class Test_get_pastes(unittest.TestCase):
    def _callFUT(self, context, request, max):
        from cluegun.views import get_pastes
        return get_pastes(context, request, max)

    def test_it(self):
        import datetime
        from cluegun.models import IPasteBin
        pb = testing.DummyModel(__provides__=IPasteBin)
        now = datetime.datetime.now()
        for x in range(0, 20):
            entry = testing.DummyModel()
            last_date = entry.date = now + datetime.timedelta(x)
            entry.author_name = 'author_name'
            pb[str(x)] = entry
        context = testing.DummyModel(__parent__=pb)
        request = testing.DummyRequest()
        result = self._callFUT(context, request, 10)
        self.assertEqual(len(result), 10)
        entry = result[0]
        self.assertEqual(entry['date'], last_date.strftime('%x at %X'))
        self.assertEqual(entry['author'], 'author_name')
        self.assertEqual(entry['url'], 'http://example.com/19')
        self.assertEqual(entry['name'], '19')

class Test_preferred_author(unittest.TestCase):
    def _callFUT(self, request):
        from cluegun.views import preferred_author
        return preferred_author(request)

    def test_with_str_author_name_in_params(self):
        request = testing.DummyRequest()
        request.params['author_name'] = 'abc'
        result = self._callFUT(request)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'abc')
        
    def test_with_unicode_author_name_in_params(self):
        request = testing.DummyRequest()
        request.params['author_name'] = u'abc'
        result = self._callFUT(request)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'abc')
        
    def test_with_str_author_name_in_cookie(self):
        request = testing.DummyRequest()
        request.cookies['cluegun.last_author'] = 'abc'
        result = self._callFUT(request)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'abc')
        
    def test_with_unicode_author_name_in_cookie(self):
        request = testing.DummyRequest()
        request.cookies['cluegun.last_author'] = u'abc'
        result = self._callFUT(request)
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'abc')
