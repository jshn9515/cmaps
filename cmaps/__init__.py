import matplotlib as mpl
from packaging import version
from typing import Optional

from .main import UniversalColormap

__version__ = '2.3.1'

if version.parse(mpl.__version__) < version.parse('3.2.0'):
    raise ImportError(f'cmaps of version {__version__} only supports matplotlib greater than 3.2.0')

repo = UniversalColormap()


def get_cmap(cname: str, *, lutsize: Optional[int] = None, reverse: bool = False):
    return repo.get_cmap(cname, lutsize=lutsize, reverse=reverse)


def get_cmap_list():
    return repo.get_cmap_list()


def plot_cmap(cname: str):
    repo.plot_cmap(cname)
