from setuptools import setup

import ducroy

__author__ = 'Johannes Schumann'
VERSION = "0.0.1"


setup(name='ducroy',
      version=VERSION,
      url='http://github.com/8me/ducroy/',
      description='DuCroy',
      author=__author__,
      author_email='jschumann@km3net.de',
      packages=['ducroy'],
      include_package_data=True,
      platforms='any',
      install_requires=[
          'pyvisa',
      ],
      entry_points={
          'console_scripts': [
          ],
      },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
      ],
)

