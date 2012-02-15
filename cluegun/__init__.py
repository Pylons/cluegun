from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from cluegun.models import appmaker

from pyramid_zodbconn import get_connection

def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())

def main(global_config, **settings):
    passwd_file = settings.get('password_file', None)
    if passwd_file is None:
        raise ValueError('password_file must not be None')
    config = Configurator(
        root_factory = root_factory,
        settings = settings,
        authentication_policy = AuthTktAuthenticationPolicy('seekrit'),
        )
    config.add_static_view('static', 'cluegun:static')
    config.scan('cluegun')
    return config.make_wsgi_app()

