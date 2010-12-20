import unittest

from pyramid import testing

class Test_get_pastes(unittest.TestCase):
    def _callFUT(self, context, request, max):
        from cluegun.views import get_pastes
        return get_pastes(context, request, max)

    def test_it(self):
        import datetime
        from cluegun.models import IPasteBin
        pb = testing.DummyResource(__provides__=IPasteBin)
        now = datetime.datetime.now()
        for x in range(0, 20):
            entry = testing.DummyResource()
            last_date = entry.date = now + datetime.timedelta(x)
            entry.author_name = 'author_name'
            pb[str(x)] = entry
        context = testing.DummyResource(__parent__=pb)
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

class Test_check_passwd(unittest.TestCase):
    def _callFUT(self, passwd_file, login, password):
        from cluegun.views import check_passwd
        return check_passwd(passwd_file, login, password)

    def test_password_equals_hashed(self):
        from StringIO import StringIO
        passwd_file = StringIO('admin:admin\n')
        result = self._callFUT(passwd_file, 'admin', 'admin')
        self.assertEqual(result, 'admin')
        
    def test_password_doesnt_equal_hashed(self):
        from StringIO import StringIO
        passwd_file = StringIO('admin:admin\n')
        result = self._callFUT(passwd_file, 'admin', 'wrongpassword')
        self.assertEqual(result, None)
        
    def test_bad_data_in_file(self):
        from StringIO import StringIO
        passwd_file = StringIO('fudge\nadmin:admin\n')
        result = self._callFUT(passwd_file, 'admin', 'admin')
        self.assertEqual(result, 'admin')

class Test_entry_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from cluegun.views import entry_view
        return entry_view(context, request)

    def test_it(self):
        import datetime
        from cluegun.models import IPasteBin
        from cluegun.views import app_version
        now = datetime.datetime.now()
        pb = testing.DummyResource(__provides__=IPasteBin)
        entry = testing.DummyResource(language='python',
                                      author_name='author_name',
                                      paste='abc',
                                      date=now,
                                      __parent__=pb)
        pb['entry'] = entry
        request = testing.DummyRequest()
        result = self._callFUT(entry, request)
        self.assertEqual(result['application_url'], 'http://example.com')
        self.assertEqual(result['author'], 'author_name')
        self.failUnless(result['style_defs'])
        self.assertEqual(result['version'], app_version)
        self.assertEqual(result['lexer_name'], 'Python')
        self.failUnless('abc' in result['paste'])
        self.assertEqual(len(result['pastes']), 1)

# XXX test the remainder of the views
