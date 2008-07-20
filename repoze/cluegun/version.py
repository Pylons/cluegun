import os

def get_version():
    f = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VERSION.txt')
    version = f.readline().strip()
    return version
