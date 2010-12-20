import sys
import urlparse

import webob
import formencode
from webob.exc import HTTPFound

import pygments
from pygments import lexers
from pygments import formatters
from pygments import util

from pyramid.traversal import find_interface
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.security import remember
from pyramid.security import forget
from pyramid.exceptions import Forbidden

from pyramid.view import view_config

from repoze.monty import marshal

from cluegun.models import PasteEntry
from cluegun.models import PasteBin
from cluegun.models import IPasteBin

app_version = '0.0'

COOKIE_LANGUAGE = 'cluegun.last_lang'
COOKIE_AUTHOR = 'cluegun.last_author'

formatter = formatters.HtmlFormatter(linenos=True, cssclass="source")
style_defs = formatter.get_style_defs()
all_lexers = list(lexers.get_all_lexers())
all_lexers.sort()
lexer_info = []
for name, aliases, filetypes, mimetypes_ in all_lexers:
    lexer_info.append({'alias':aliases[0], 'name':name})

# utility functions

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

def preferred_author(request):
    author_name = request.params.get('author_name', u'')
    if not author_name:
        author_name = request.cookies.get(COOKIE_AUTHOR, u'')
    if isinstance(author_name, str):
        author_name = unicode(author_name, 'utf-8')
    return author_name

def check_passwd(passwd_file, login, password):
    if not hasattr(passwd_file, 'read'):
        passwd_file = open(passwd_file, 'r')
    for line in passwd_file:
        try:
            username, hashed = line.rstrip().split(':', 1)
        except ValueError:
            continue
        if username == login:
            if password == hashed:
                return username
    return None

# views and schemas

@view_config(context=PasteEntry, permission='view',
             renderer='templates/entry.pt')
def entry_view(context, request):
    paste = context.paste or u''
    try:
        if context.language:
            l = lexers.get_lexer_by_name(context.language)
        else:
            l = lexers.guess_lexer(context.paste)
        l.aliases[0]
    except util.ClassNotFound:
        # couldn't guess lexer
        l = lexers.TextLexer()

    formatted_paste = pygments.highlight(paste, l, formatter)
    pastes = get_pastes(context, request, 10)

    return dict(
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

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste = formencode.validators.NotEmpty()

@view_config(context=PasteBin, permission='view', renderer='templates/index.pt')
def index_view(context, request):
    params = request.params
    author_name = preferred_author(request)
    language = u''
    paste = u''
    message = u''
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
            schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            response = webob.Response()
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
            return HTTPFound(location='%s/%s' % (app_url, pasteid))

    pastes = get_pastes(context, request, 10)

    return dict(
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

@view_config(name='manage', context=PasteBin, permission='manage',
             renderer='templates/manage.pt')
def manage_view(context, request):
    params = request.params
    app_url = request.application_url

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        return HTTPFound(location=app_url)

    pastes = get_pastes(context, request, sys.maxint)

    return dict(
        version = app_version,
        pastes = pastes,
        application_url = app_url,
        )
        
@view_config(context=Forbidden, renderer='templates/login.pt')
@view_config(context=PasteBin, name='login', renderer='templates/login.pt')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        password_file = request.registry.settings['password_file']
        if check_passwd(password_file, login, password):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )
    
@view_config(name='logout', context=PasteBin, permission='view')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context),
                     headers = headers)
    

