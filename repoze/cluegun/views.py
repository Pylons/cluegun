import os
import urlparse

import formencode
import webob

from paste import urlparser

import pygments
from pygments import lexers
from pygments import formatters
from pygments import util


from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.template import render_template_to_response
from repoze.bfg.template import render_template
from repoze.bfg.traversal import find_interface

from repoze.cluegun.models import PasteEntry
from repoze.cluegun.models import IPasteBin
from repoze.cluegun.version import get_version

app_version = get_version()

COOKIE_LANGUAGE = 'cluebin.last_lang'
COOKIE_AUTHOR = 'cluebin.last_author'

here = os.path.abspath(os.path.dirname(__file__))
static = urlparser.StaticURLParser(os.path.join(here, 'static', '..'))

@wsgiapp
def static_view(environ, start_response):
    return static(environ, start_response)

def get_pastes(context, request):
    pastebin = find_interface(context, IPasteBin)
    pastes = []
    app_url = request.application_url
    for name, entry in pastebin.items():
        if entry.date is not None:
            pdate = entry.date.strftime('%x at %X')
        else:
            pdate = 'UNKNOWN'
        paste_url = urlparse.urljoin(app_url, name)
        new = {'author':entry.author_name, 'date':pdate, 'url':paste_url}
        pastes.append(new)
    return pastes

def entry_view(context, request):
    paste = context.paste or u''
    try:
        if context.language:
            l = lexers.get_lexer_by_name(context.language)
        else:
            l = lexers.guess_lexer(context.paste)
        language = l.aliases[0]
    except util.ClassNotFound, err:
        # couldn't guess lexer
        l = lexers.TextLexer()
    formatter = formatters.HtmlFormatter(linenos=True,
                                         cssclass="source")
    formatted_paste = pygments.highlight(paste, l, formatter)
    pastes = get_pastes(context, request)

    inner = render_template('templates/view.pt',
                            style_defs=formatter.get_style_defs(),
                            lexer_name=l.name,
                            paste=formatted_paste,
                            pastes=pastes)

    return render_template_to_response(
        'templates/index.pt',
        version = app_version,
        body = inner,
        message = None,
        application_url = request.application_url,
        )

def preferred_language(request):
    language = request.cookies.get(COOKIE_LANGUAGE, u'')
    if isinstance(language, str):
        language = unicode(language, 'utf-8')
    return language

def preferred_author(request):
    author_name = request.params.get('author_name', u'')
    if not author_name:
        author_name = request.cookies.get(COOKIE_AUTHOR, u'')
    if isinstance(author_name, str):
        author_name = unicode(author_name, 'utf-8')
    return author_name

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste = formencode.validators.NotEmpty()

def index_view(context, request):
    params = request.params
    author_name = preferred_author(request)
    language = preferred_language(request)
    paste = u''
    message = u''
    response = webob.Response()

    if params.has_key('form.submitted'):
        paste = request.params.get('paste', '')
        author_name = request.params.get('author_name', '')
        language = request.params.get('language', '')
        schema = PasteAddSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            response.set_cookie(COOKIE_AUTHOR, author_name)
            response.set_cookie(COOKIE_LANGUAGE, language)

            if isinstance(author_name, str):
                author_name = unicode(author_name, 'utf-8')
            if isinstance(language, str):
                language = unicode(language, 'utf-8')
            if isinstance(paste, str):
                paste = unicode(paste, 'utf-8')

            pobj = PasteEntry(author_name, paste, language)
            pasteid = context.add_paste(pobj)
            response.status = '301 Moved Permanently'
            response.headers['Location'] = '/%s' % pasteid

    all = list(lexers.get_all_lexers())
    all.sort()
    our_lexers = []
    for name, aliases, filetypes, mimetypes_ in all:
        selected = False
        if language == aliases[0]:
            selected = True
        our_lexers.append({'selected':selected, 'alias':aliases[0],
                           'name':name})

    pastes = get_pastes(context, request)

    formadd =  render_template('templates/add.pt', author_name=author_name,
                               paste=paste, lexers=our_lexers,
                               pastes=pastes)

    body = render_template(
        'templates/index.pt',
        version = app_version,
        body = formadd,
        message = message,
        pastes = pastes,
        application_url = request.application_url,
        )
    response.unicode_body = unicode(body)
    return response

        

