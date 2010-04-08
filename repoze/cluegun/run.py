def make_app(global_config, **kw):
    from repoze.bfg.configuration import Configurator
    from repoze.cluegun.models import appmaker
    db_path = kw.get('db_path', None)
    if db_path is None:
        raise ValueError('db_path must not be None')        
    from repoze.zodbconn.finder import PersistentApplicationFinder
    finder = PersistentApplicationFinder('file://%s' % db_path, appmaker)
    config = Configurator(root_factory=finder, settings=kw)
    config.begin()
    config.load_zcml('repoze.cluegun:configure.zcml')
    config.end()
    app = config.make_wsgi_app()
    return app

