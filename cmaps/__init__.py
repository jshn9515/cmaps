import matplotlib as mpl
from packaging import version

from .main import UniversialColormap

__version__ = '2.1.0'

if version.parse(mpl.__version__) < version.parse('3.2.0'):
    raise ImportError(f'cmaps of version {__version__} only supports matplotlib greater than 3.2.0')

repo = UniversialColormap()

def get_cmap(cname: str):
    return repo.get_cmap(cname)

def get_cmap_list():
    return repo.get_cmap_list()

def plot_cmap(cname: str):
    return repo.plot_cmap(cname)
