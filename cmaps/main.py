import glob
import os
import pickle
import re
from typing import Any, Iterable

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt


def find_files_with_extension(directory: str, extension: str) -> list[str]:
    found_files = []
    for root, _, _ in os.walk(directory):
        found_files.extend(glob.glob(os.path.join(root, extension)))
    return sorted(found_files)


CMAPS_FILE_DIR = os.getenv(
    'CMAPS_FILE_DIR',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'colormaps'),
)


class ListedColormap(colors.Colormap):
    def __init__(self, colors: Iterable, name: str = 'from_list', N: int | None = None):
        """
        Colormap object generated from a list of colors.

        This may be most useful when indexing directly into a colormap,
        but it can also be used to generate special colormaps for ordinary
        mapping.

        Parameters
        ----------
        colors : str, list, array
            Sequence of Matplotlib color specifications (color names or RGB(A) values).
        name : str, optional
            String to identify the colormap.
        N : int, optional
            Number of entries in the map. The default is *None*, in which case
            there is one colormap entry for each element in the list of colors.
            If ::

                N < len(colors)

            the list will be truncated at *N*.
            If ::

                N > len(colors)

            the list will be extended by repetition.
        """
        self.colors: npt.NDArray[Any]
        self.monochrome: bool = False
        if isinstance(colors, (list, tuple, np.ndarray)):
            self.colors = np.asarray(colors)
            if N:
                if N < len(colors):
                    self.colors = self.colors[:N]
                elif N > len(colors):
                    self.colors = np.repeat(self.colors, N // len(colors) + 1, axis=0)[:N]
            N = len(self.colors)
        elif isinstance(colors, str):
            if N is None:
                raise ValueError('N must be specified when colors is a string')
            self.colors = np.array([colors] * N)
            self.monochrome = True
        else:
            raise TypeError('Incorrect input type for colors')
        super().__init__(name=name, N=N)

    def _init(self):
        self._lut = np.zeros((self.N + 3, 4), dtype=float)
        self._lut[:-3] = colors.to_rgba_array(self.colors)
        self._isinit = True
        self._set_extremes()  # type: ignore

    def resampled(self, lutsize: int) -> 'ListedColormap':
        """
        Return a resampled instance of the Colormap.

        Parameters
        ----------
        lutsize : int
            The number of color for the resampled colormap.

        Returns
        -------
        ListedColormap
            A resampled instance of the colormap.
        """
        colors = self(np.linspace(0, 1, lutsize))
        new_cmap = ListedColormap(colors, name=self.name)
        new_cmap.set_extremes(bad=self._rgba_bad, under=self._rgba_under, over=self._rgba_over)  # type: ignore
        return new_cmap

    def reversed(self, name: str | None = None) -> 'ListedColormap':
        """
        Return a reversed instance of the Colormap.

        Parameters
        ----------
        name : str, optional
            The name for the reversed colormap. If None, the
            name is set to ``self.name + '_r'``.

        Returns
        -------
        ListedColormap
            A reversed instance of the colormap.
        """
        if name is None:
            name = self.name + '_r'
        colors_r = np.flipud(self.colors)
        new_cmap = ListedColormap(colors_r, name=name, N=self.N)
        new_cmap.set_extremes(
            bad=self._rgba_bad, under=self._rgba_under, over=self._rgba_over  # type: ignore
        )
        return new_cmap

    def interp(self, lutsize: int) -> 'ListedColormap':
        """
        Interpolate the colormap to a new size.

        Different from resampled of the new version of matplotlib (we interpolate colors here)

        Parameters
        ----------
        lutsize : int
            The number of color for the interpolated colormap.

        Returns
        -------
        ListedColormap
            A interpolated instance of the colormap.
        """
        x = np.linspace(0, 1, lutsize)
        xp = np.linspace(0, 1, self.N)
        new_cmap = np.hstack(
            [
                np.interp(x, xp, self.colors[:, i]).reshape(-1, 1)
                for i in range(self.colors.shape[1])
            ]
        )
        return ListedColormap(new_cmap, name='interp_' + self.name)

    def __add__(self, other: 'ListedColormap') -> 'ListedColormap':
        return ListedColormap(
            np.vstack([self.colors, other.colors]), name=self.name + '_' + other.name
        )

    def __iadd__(self, other: 'ListedColormap') -> 'ListedColormap':
        return self + other

    def __mul__(self, num: int) -> 'ListedColormap':
        return ListedColormap(
            np.repeat(self.colors, num, axis=0), name=self.name + f'_rep({str(num)})'
        )

    def __imul__(self, num: int) -> 'ListedColormap':
        return self * num

    def __getitem__(self, item: Any) -> 'ListedColormap':
        return ListedColormap(self.colors[item], name=self.name + '_slice')

    def __str__(self) -> str:
        return str(self.colors)

    def __len__(self) -> int:
        return self.N

    def __iter__(self):
        return iter(self.colors)

    def __next__(self):
        return next(self)

    def to_list(self) -> list[Any]:
        return self.colors.tolist()

    def to_numpy(self) -> npt.NDArray[Any]:
        return self.colors

    def to_segment(self, N: int | None = None) -> colors.LinearSegmentedColormap:
        if N is None:
            N = self.N
        return colors.LinearSegmentedColormap.from_list(
            'seg_' + self.name, self.colors.tolist(), N=N
        )

    def plot_cmap(self, show: bool = True):
        a = np.outer(np.ones(10), np.arange(0, 1, 0.001))
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(a, aspect='auto', cmap=self, origin='lower')
        ax.text(
            x=0.5,
            y=0.5,
            s=self.name,
            verticalalignment='center',
            horizontalalignment='center',
            fontsize=14,
            transform=ax.transAxes,
        )
        ax.axis('off')
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
        if show:
            plt.show()


class UniversalColormap:
    def __init__(self, path: str | None = None):
        """Constructor for UniversalColormap class. File path to the color maps is required."""
        cmap_name_list = set(
            [cname for cname in mpl.colormaps if not cname.endswith('_r')]
        )

        if path is None:  # use the default color maps
            cmap_file_dict = find_files_with_extension(CMAPS_FILE_DIR, '*.pkl')
            cmap_file_list = find_files_with_extension(CMAPS_FILE_DIR, '*.rgb')
        else:
            cmap_file_dict = []
            cmap_file_list = sorted(glob.glob(os.path.join(path, '*.rgb')))

        if len(cmap_file_dict) > 0:
            for cmap_file in cmap_file_dict:
                with open(cmap_file, 'rb') as fp:
                    color_data: dict = pickle.load(fp)
                for cname, colors in color_data.items():
                    try:
                        cmap = ListedColormap(colors, name=cname)
                        mpl.colormaps.register(name=cname, cmap=cmap)
                        cmap_name_list.add(cname)
                    except ValueError:
                        pass

        for cmap_file in cmap_file_list:
            cname = os.path.splitext(os.path.basename(cmap_file))[0]
            # start with the number will result illegal attribute
            if cname[0].isdigit() or cname.startswith('_'):
                cname = 'C' + cname
            if '-' in cname:
                cname = 'cmaps_' + cname.replace('-', '_')
            if '+' in cname:
                cname = 'cmaps_' + cname.replace('+', '_')

            try:
                cmap = ListedColormap(self._color_table(cmap_file), name=cname)
                mpl.colormaps.register(name=cname, cmap=cmap)
                cmap_name_list.add(cname)
            except ValueError:
                pass

        self.cmap_name_list = sorted(list(cmap_name_list))

    def _color_table(self, cmap_file: str) -> npt.NDArray[Any]:
        pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*).*')
        with open(cmap_file) as cmap:
            cmap_buff = cmap.read()
        cmap_buff = re.sub(r'ncolors.*\n', '', cmap_buff)
        if re.search(r'\s*\d\.\d*', cmap_buff):
            return np.asarray(pattern.findall(cmap_buff), dtype='f4')
        else:
            return np.asarray(pattern.findall(cmap_buff), dtype='u1') / 255.0

    def get_cmap(
        self, cname: str, *, lutsize: int | None = None, reverse: bool = False
    ) -> ListedColormap:
        cmap: ListedColormap = plt.get_cmap(cname)  # type: ignore
        if lutsize:
            cmap = cmap.interp(lutsize)
        if reverse:
            cmap = cmap.reversed()
        return cmap

    def get_cmap_list(self) -> list[str]:
        return self.cmap_name_list

    def plot_cmap(
        self,
        cname: str,
        *,
        lutsize: int | None = None,
        reverse: bool = False,
        show: bool = True,
    ):
        cmap = self.get_cmap(cname, lutsize=lutsize, reverse=reverse)
        a = np.outer(np.ones(10), np.arange(0, 1, 0.001))
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(a, aspect='auto', cmap=cmap, origin='lower')
        ax.text(
            x=0.5,
            y=0.5,
            s=cmap.name,
            verticalalignment='center',
            horizontalalignment='center',
            fontsize=14,
            transform=ax.transAxes,
        )
        ax.axis('off')
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
        if show:
            plt.show()
