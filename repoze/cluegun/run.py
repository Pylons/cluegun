def make_app(global_config, db_path=None):
    # paster app config callback
    from repoze.bfg import make_app
    from repoze.cluegun.models import PersistentRootFinder as finder
    if db_path is None:
        raise ValueError('db_path must not be None')
    get_root = finder(db_path)
    import repoze.cluegun
    app = make_app(get_root, repoze.cluegun)
    return app

if __name__ == '__main__':
    from paste import httpserver
    app = make_app(None)
    httpserver.serve(app, host='0.0.0.0', port='5432')
    
