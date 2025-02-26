import matplotlib as mpl
from packaging import version

from .main import UniversalColormap

__version__ = '3.0.0'

if version.parse(mpl.__version__) < version.parse('3.2.0'):
    raise ImportError(
        f'cmaps of version {__version__} only supports matplotlib greater than 3.2.0'
    )

repo = UniversalColormap()


def get_cmap(cname: str, *, lutsize: int | None = None, reverse: bool = False):
    if cname.endswith('_r'):
        return repo.get_cmap(cname[:-2], lutsize=lutsize, reverse=True)
    return repo.get_cmap(cname, lutsize=lutsize, reverse=reverse)


def get_cmap_list():
    return repo.get_cmap_list()


def plot_cmap(
    cname: str,
    *,
    lutsize: int | None = None,
    reverse: bool = False,
    show: bool = True,
):
    if cname.endswith('_r'):
        repo.plot_cmap(cname[:-2], lutsize=lutsize, reverse=True, show=show)
    else:
        repo.plot_cmap(cname, lutsize=lutsize, reverse=reverse, show=show)
