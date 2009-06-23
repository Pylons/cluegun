import os
import sys
import urlparse

import formencode
import webob

from paste import urlparser

import pygments
from pygments import lexers
from pygments import formatters
from pygments import util

from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.traversal import find_interface
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.monty import marshal

from repoze.cluegun.models import PasteEntry
from repoze.cluegun.models import IPasteBin

app_version = '0.3dev'

COOKIE_LANGUAGE = 'cluebin.last_lang'
COOKIE_AUTHOR = 'cluebin.last_author'

here = os.path.abspath(os.path.dirname(__file__))
static = urlparser.StaticURLParser(os.path.join(here, 'static', '..'))

@wsgiapp
def static_view(environ, start_response):
    return static(environ, start_response)

def get_pastes(context, request, max):
    pastebin = find_interface(context, IPasteBin)
    pastes = []
    app_url = request.application_url
    keys = list(pastebin.keys())
    def byint(a, b):
        try:
            return cmp(int(a), int(b))
        except TypeError:
            return cmp(a, b)
    keys.sort(byint)
    keys.reverse()
    keys = keys[:max]
    for name in keys:
        entry = pastebin[name]
        if entry.date is not None:
            pdate = entry.date.strftime('%x at %X')
        else:
            pdate = 'UNKNOWN'
        paste_url = urlparse.urljoin(app_url, name)
        new = {'author':entry.author_name, 'date':pdate, 'url':paste_url,
               'name':name}
        pastes.append(new)
    return pastes

formatter = formatters.HtmlFormatter(linenos=True,
                                     cssclass="source")
style_defs = formatter.get_style_defs()

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

    formatted_paste = pygments.highlight(paste, l, formatter)
    pastes = get_pastes(context, request, 10)

    return render_template_to_response(
        'templates/entry.pt',
        author = context.author_name,
        date = context.date.strftime('%x at %X'),
        style_defs = style_defs,
        lexer_name = l.name,
        paste = formatted_paste,
        pastes = pastes,
        version = app_version,
        message = None,
        application_url = request.application_url,
        )

def preferred_author(request):
    author_name = request.params.get('author_name', u'')
    if not author_name:
        author_name = request.cookies.get(COOKIE_AUTHOR, u'')
    if isinstance(author_name, str):
        author_name = unicode(author_name, 'utf-8')
    return author_name

all_lexers = list(lexers.get_all_lexers())
all_lexers.sort()
lexer_info = []
for name, aliases, filetypes, mimetypes_ in all_lexers:
    lexer_info.append({'alias':aliases[0], 'name':name})

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste = formencode.validators.NotEmpty()

def index_view(context, request):
    params = request.params
    author_name = preferred_author(request)
    language = u''
    paste = u''
    message = u''
    response = webob.Response()
    app_url = request.application_url
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

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
            response.headers['Location'] = '%s/%s' % (app_url, pasteid)

    pastes = get_pastes(context, request, 10)

    body = render_template(
        'templates/index.pt',
        author_name = author_name,
        paste = paste,
        lexers = lexer_info,
        version = app_version,
        message = message,
        pastes = pastes,
        application_url = app_url,
        user = user,
        can_manage = can_manage,
        )
    response.unicode_body = unicode(body)
    return response

def manage_view(context, request):
    params = request.params
    message = u''
    response = webob.Response()
    app_url = request.application_url

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        message = '%s pastes deleted' % len(checkboxes)
        response.status = '301 Moved Permanently'
        response.headers['Location'] = app_url

    pastes = get_pastes(context, request, sys.maxint)

    body = render_template(
        'templates/manage.pt',
        version = app_version,
        pastes = pastes,
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response
        
def logout_view(context, request):
    response = webob.Response()
    response.status = '401 Unauthorized'
    return response

    
