import setuptools
from cmaps import __version__

setuptools.setup(
    name='cmaps',
    description='An extension of matplotlib colormaps',
    version=__version__,
    author='Hao Huang',
    author_email='hhuangwx@gmail.com',
    maintainer='jshn9515',
    maintainer_email='jshn9510@gmail.com',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        'cmaps': [
            'colormaps/ncar_ncl/*',
            'colormaps/matlab/*',
            'colormaps/self_defined/*',
        ],
    },
    license='GPL-v3.0',
    install_requires=['numpy', 'matplotlib>=3.2.0', 'packaging'],
)
