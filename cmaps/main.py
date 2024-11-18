import os
import re
import glob
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from typing import List, Optional


def find_files_with_extension(directory: str, extension: str):
    found_files = []
    for root, _, _ in os.walk(directory):
        found_files.extend(glob.glob(os.path.join(root, extension)))
    return found_files


CMAPS_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'colormaps')


class SliceColormap(ListedColormap):
    def __add__(self, other: ListedColormap) -> 'SliceColormap':
        return SliceColormap(np.vstack([self.colors, other.colors]), name=self.name + '_' + other.name)
    
    def __getitem__(self, item) -> 'SliceColormap':
        colors = np.asarray(self.colors)
        return SliceColormap(colors[item], name=self.name + '_slice')
    
    def __str__(self) -> str:
        colors = np.asarray(self.colors)
        return str(colors)
    
    def to_list(self) -> List:
        colors = np.asarray(self.colors)
        return colors.tolist()
    
    def to_numpy(self) -> np.ndarray:
        return np.asarray(self.colors)
    
    def plot_cmap(self) -> None:
        a = np.outer(np.ones(10), np.arange(0, 1, 0.001))
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(a, aspect='auto', cmap=self, origin='lower')
        ax.text(0.5, 0.5, self.name, verticalalignment='center', horizontalalignment='center', 
                fontsize=12, transform=ax.transAxes)
        ax.axis('off')
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
        plt.show()


class UniversialColormap:
    def __init__(self, path: Optional[str] = None):
        """ Constructor for UniversialColormap class. File path to the color maps is required. """
        cmap_name_list = set()
        if path is None:
            USER_CMAP_FILES = find_files_with_extension(CMAPS_FILE_DIR, '*.rgb')
            cmap_file_list = sorted(USER_CMAP_FILES)
        else:
            cmap_file_list = sorted(glob.glob(os.path.join(path, '*.rgb')))
        for cmap_file in cmap_file_list:
            cname = os.path.basename(cmap_file).split('.rgb')[0]
            # start with the number will result illegal attribute
            if cname[0].isdigit() or cname.startswith('_'):
                cname = 'C' + cname
            if '-' in cname:
                cname = 'cmaps_' + cname.replace('-', '_')
            if '+' in cname:
                cname = 'cmaps_' + cname.replace('+', '_')

            try:
                cmap = mpl.colormaps.get_cmap(cname)
            except ValueError:
                cmap = SliceColormap(self._color_table(cmap_file), name=cname)
                mpl.colormaps.register(name=cname, cmap=cmap)
            setattr(self, cname, cmap)
            cmap_name_list.add(cname)

            cname = cname + '_r'
            try:
                cmap = mpl.colormaps.get_cmap(cname)
            except ValueError:
                cmap = SliceColormap(self._color_table(cmap_file)[::-1], name=cname)
                mpl.colormaps.register(name=cname, cmap=cmap)
            setattr(self, cname, cmap)
            cmap_name_list.add(cname)
        self.cmap_name_list = sorted(list(cmap_name_list))

    def _color_table(self, cmap_file: str) -> np.ndarray:
        pattern = re.compile(r'(\d\.?\d*)\s+(\d\.?\d*)\s+(\d\.?\d*).*')
        with open(cmap_file) as cmap:
            cmap_buff = cmap.read()
        cmap_buff = re.sub(r'ncolors.*\n', '', cmap_buff)
        if re.search(r'\s*\d\.\d*', cmap_buff):
            return np.asarray(pattern.findall(cmap_buff), 'f4')
        else:
            return np.asarray(pattern.findall(cmap_buff), 'u1') / 255.0

    def get_cmap(self, cname: str) -> SliceColormap:
        return getattr(self, cname)

    def get_cmap_list(self) -> List[str]:
        return self.cmap_name_list
    
    def plot_cmap(self, cname: str) -> None:
        a = np.outer(np.ones(10), np.arange(0, 1, 0.001))
        fig = plt.figure(1)
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(a, aspect='auto', cmap=getattr(self, cname), origin='lower')
        ax.text(0.5, 0.5, cname, verticalalignment='center', horizontalalignment='center', 
                fontsize=12, transform=ax.transAxes)
        ax.axis('off')
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
        plt.show()
