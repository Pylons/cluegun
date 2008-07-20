import os
import webob

from StringIO import StringIO
import pygments
from pygments import lexers
from pygments import formatters
from pygments import util
from xml.sax import saxutils
from paste.urlparser import StaticURLParser

from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.template import render_template_to_response

from repoze.cluegun import paste as pastebase
from repoze.cluegun import utils
from repoze.cluegun.version import get_version

here = os.path.abspath(os.path.dirname(__file__))
static = StaticURLParser(os.path.join(here, 'static'))

@wsgiapp
def static_view(environ, start_response):
    return static(environ, start_response)

class IndexView:
    """Repoze.bfg view factory representing a pastebin.

      >>> view = IndexView()
    """
    COOKIE_LANGUAGE = 'cluebin.last_lang'
    COOKIE_AUTHOR = 'cluebin.last_author'

    def __init__(self):
        self.pmanager = pastebase.PasteManager()
        self.version = get_version()

    def __call__(self, context, request):
        response = webob.Response(content_type='text/html')
        environ = request.environ

        out = StringIO()

        handler = self.index
        pieces = [x for x in environ['PATH_INFO'].split('/') if x]
        if pieces and hasattr(self, pieces[0]):
            handler = getattr(self, pieces[0])

        handler(request, response, out, *pieces[1:])
        if response.status_int != 200:
            return response

        wrapped = out.getvalue()
        return render_template_to_response('static/index.pt', body=wrapped,
                                           version=self.version)

    def paste_listing(self, request, response, out):
        print >> out, u'<fieldset><legend>Previous Pastes</legend><ul>'

        for pobj in self.pmanager.get_pastes():
            if pobj.date is not None:
                pdate = pobj.date.strftime('%x at %X')
            else:
                pdate = 'UNKNOWN'
            print >> out, u'<li><a href="%s">Post by: %s on %s</a></li>' % \
                  (utils.url(request, 'pasted/%i' % pobj.pasteid),
                   pobj.author_name, pdate)

        print >> out, u'</ul></fieldset>'

    def preferred_author(self, request):
        author_name = request.params.get('author_name', u'')
        if not author_name:
            author_name = request.cookies.get(self.COOKIE_AUTHOR, u'')
        if isinstance(author_name, str):
            author_name = unicode(author_name, 'utf-8')
        return author_name

    def preferred_language(self, request):
        language = request.cookies.get(self.COOKIE_LANGUAGE, u'')
        if isinstance(language, str):
            language = unicode(language, 'utf-8')

    def index(self, request, response, out, msg=u'', paste_obj=None):
        if msg:
            msg = u'<div class="message">%s</div>' % msg

        paste = u''
        language = self.preferred_language(request)
        if paste_obj is not None:
            paste = paste_obj.paste or u''
            try:
                if paste_obj.language:
                    l = lexers.get_lexer_by_name(paste_obj.language)
                else:
                    l = lexers.guess_lexer(paste_obj.paste)
                language = l.aliases[0]
            except util.ClassNotFound, err:
                # couldn't guess lexer
                l = lexers.TextLexer()
            formatter = formatters.HtmlFormatter(linenos=True,
                                                 cssclass="source")
            formatted_paste = pygments.highlight(paste, l, formatter)

            print >> out, u'''
              <style>%s</style>
              <dl class="previous_paste">
              <dt>Previous Paste</dt>
              <dd>Format: %s</dd>
              <dd>%s</dd>
              </dl>
            ''' % (formatter.get_style_defs(), l.name, formatted_paste)

        lexer_options = u'<option value="">-- Auto-detect --</option>'
        all = [x for x in lexers.get_all_lexers()]
        all.sort()
        for name, aliases, filetypes, mimetypes_ in all:
            selected = u''
            if language == aliases[0]:
                selected = u' selected'
            lexer_options += u'<option value="%s"%s>%s</option>' % (aliases[0],
                                                                    selected,
                                                                    name)

        print >> out, u'''
            %s
            <div class="left">
            ''' % msg

        print >> out, u'''
            <form action="%(action)s" method="POST">
              <fieldset>
                <legend>Paste Info</legend>
                <div class="field">
                  <label for="author_name">Name</label>
                  <input type="text" name="author_name" value="%(author_name)s" />
                </div>
                <div class="field">
                  <label for="language">Language</label>
                  <select name="language">
%(lexers)s
                  </select>
                </div>
                <div class="field">
                  <label for="paste">Paste Text</label>
                  <textarea name="paste">%(paste)s</textarea>
                </div>
                <input type="submit" />
              </fieldset>
            </form>
            </div>
        ''' % {'action': utils.url(request, 'paste'),
               'paste': saxutils.escape(paste),
               'lexers': lexer_options,
               'author_name': self.preferred_author(request)}

        print >> out, u'<div class="right">'
        self.paste_listing(request, response, out)
        print >> out, u'</div>'

    def pasted(self, request, response, out, *args):
        pobj = self.pmanager.get_paste(args[0])
        self.index(request, response, out, paste_obj=pobj)

    def paste(self, request, response, out):
        if not request.params.get('paste', None):
            self.index(request, response, out,
                       msg=u"* You did not fill in body")
        else:
            paste = request.params['paste']
            author_name = request.params['author_name']
            language = request.params['language']
            response.set_cookie(self.COOKIE_AUTHOR, author_name)
            response.set_cookie(self.COOKIE_LANGUAGE, language)

            if isinstance(author_name, str):
                author_name = unicode(author_name, 'utf-8')
            if isinstance(language, str):
                language = unicode(language, 'utf-8')
            if isinstance(paste, str):
                paste = unicode(paste, 'utf-8')

            pobj = self.pmanager.save_paste(author_name, paste, language)

            newurl = utils.url(request, 'pasted/%s' % str(pobj.pasteid))

            response.status = '301 Moved Permanently'
            response.headers['Location'] = newurl

index_view = IndexView()

