import setuptools
from cmaps import __version__


setuptools.setup(
    name='cmaps',
    description='An extension of matplotlib colormaps',
    version=__version__,
    author='jshn9515',
    author_email='jshn9515@163.com',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        'cmaps': [
            'colormaps/ncar_ncl/*',
            'colormaps/self_defined/*',
            'colormaps.png',
        ],
    },
    license='MIT',
    install_requires=['numpy', 'matplotlib>=3.2.0', 'packaging'],
)
