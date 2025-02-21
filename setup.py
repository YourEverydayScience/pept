#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#    pept is a Python library that unifies Positron Emission Particle
#    Tracking (PEPT) research, including tracking, simulation, data analysis
#    and visualisation tools
#
#    Copyright (C) 2019 Andrei Leonard Nicusan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# File   : setup.py
# License: GNU v3.0
# Author : Andrei Leonard Nicusan <a.l.nicusan@bham.ac.uk>
# Date   : 23.08.2019

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev


import  io
import  os
import  sys
import  warnings
from    shutil              import  rmtree

from    setuptools          import  find_packages, setup, Command, Extension


try:
    import  numpy               as      np
    from    Cython.Build        import  cythonize
    from    Cython.Distutils    import  build_ext
except ImportError as e:
    warnings.warn(e.args[0])
    warnings.warn('The pept package requires Cython and numpy to be pre-installed')
    raise ImportError('Cython or numpy not found! Please install cython and numpy (or run pip install -r requirements.txt) and try again')


# Package meta-data.
NAME = 'pept'
DESCRIPTION = 'A Python library that unifies Positron Emission Particle Tracking (PEPT) research, including tracking, simulation, data analysis and visualisation tools.'
URL = 'https://github.com/uob-positron-imaging-centre/pept'
EMAIL = 'a.l.nicusan@bham.ac.uk'
AUTHOR = 'Andrei Leonard Nicusan'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.2'


def requirements():
    # The dependencies are the same as the contents of requirements.txt
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip()]


# What packages are required for this module to be executed?
REQUIRED = requirements()


# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}


cythonize_kw = dict(language_level = 3)
cy_extension_kw = dict()

extra_compile_args = ['-O3']
cy_extension_kw['extra_compile_args'] = extra_compile_args
cy_extension_kw['include_dirs'] = [np.get_include()]

cy_extensions = [
    Extension('pept.tracking.peptml.extensions.find_cutpoints_api',
              ['pept/tracking/peptml/extensions/find_cutpoints_api.pyx'],
              **cy_extension_kw),
    Extension('pept.scanners.modular_camera.extensions.get_pept_event',
              ['pept/scanners/modular_camera/extensions/get_pept_event.pyx'],
              **cy_extension_kw),
]

extensions = cythonize(cy_extensions, **cythonize_kw)


# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name = NAME,
    version = about['__version__'],
    description = DESCRIPTION,
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = AUTHOR,
    author_email = EMAIL,
    python_requires = REQUIRES_PYTHON,
    url = URL,
    packages = find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # entry_points = {
    #     'console_scripts': ['mycli = mymodule:cli'],
    # },
    install_requires = REQUIRED,
    extras_require = EXTRAS,
    include_package_data = True,
    keywords = 'pept positron emission particle tracking',
    license = 'GNU',
    classifiers = [
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Cython',
        'Programming Language :: C',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    # $ setup.py publish support.
    cmdclass = {
        'upload': UploadCommand,
        'build_ext': build_ext
    },
    ext_modules = extensions
)
