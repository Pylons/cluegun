from pyramid.configuration import Configurator
from cluegun.models import appmaker

def main(global_config, **settings):
    db_path = settings.get('db_path', None)
    if db_path is None:
        raise ValueError('db_path must not be None')        
    from repoze.zodbconn.finder import PersistentApplicationFinder
    finder = PersistentApplicationFinder('file://%s' % db_path, appmaker)
    config = Configurator(root_factory=finder, settings=settings)
    config.load_zcml('cluegun:configure.zcml')
    return config.make_wsgi_app()

