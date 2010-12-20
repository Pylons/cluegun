from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from cluegun.models import appmaker

from repoze.zodbconn.finder import PersistentApplicationFinder

def main(global_config, **settings):
    db_path = settings.get('db_path', None)
    if db_path is None:
        raise ValueError('db_path must not be None')
    passwd_file = settings.get('password_file', None)
    if passwd_file is None:
        raise ValueError('password_file must not be None')
    root_factory = PersistentApplicationFinder('file://%s' % db_path, appmaker)
    config = Configurator(
        root_factory = root_factory,
        settings = settings,
        authentication_policy = AuthTktAuthenticationPolicy('seekrit'),
        )
    config.add_static_view('static', 'cluegun:static')
    config.scan('cluegun')
    return config.make_wsgi_app()

