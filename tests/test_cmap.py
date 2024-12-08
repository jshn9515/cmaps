import cmaps
import pytest
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def test_cmap_list():
    a = cmaps.get_cmap_list()
    for i in a:
        assert not i.endswith('_r')

def test_get_cmap():
    a = cmaps.get_cmap('testcmap', lutsize=16)
    b = cmaps.get_cmap('testcmap', lutsize=16, reverse=True)
    c = cmaps.get_cmap('testcmap_r', lutsize=16)
    assert np.allclose(np.flipud(a.to_numpy()), b.to_numpy())
    assert np.allclose(b.to_numpy(), c.to_numpy())
    with pytest.raises(ValueError):
        cmaps.get_cmap('badcmap')
    with pytest.raises(ValueError):
        cmaps.get_cmap('testcmap', lutsize=-1)

def test_cmap_calc():
    a = cmaps.get_cmap('testcmap', lutsize=128)
    b = a[10:100:4]
    c = a[100:10:-2]
    d = a + b * 2 + c
    
def test_cmap_iter():
    a = cmaps.get_cmap('testcmap', lutsize=128)
    for i in a:
        assert isinstance(i, np.ndarray)

def test_cmap_export():
    a = cmaps.get_cmap('testcmap', lutsize=128)
    assert isinstance(a.to_list(), list)
    assert isinstance(a.to_numpy(), np.ndarray)
    assert isinstance(a.to_segment(), LinearSegmentedColormap)

def test_cmap_plot():
    cmaps.plot_cmap('testcmap', lutsize=64, show=False)
    cmaps.plot_cmap('testcmap_r', lutsize=64, show=False)
    a = cmaps.get_cmap('testcmap', lutsize=128)
    a.plot_cmap(show=False)
    plt.close('all')


if __name__ == '__main__':
    pytest.main()
