#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=exec-used,broad-except

""" Build dsml_model as a package for distribution. """

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import json
import os
import sys
import tarfile
from datetime import datetime
from shutil import copyfile, rmtree

import setuptools.command.sdist as sdist
from setuptools import Command, find_packages, setup


# Package meta-data.
NAME = 'pybadges'
DESCRIPTION = 'Modified pybadges for Sophos AI'
AUTHOR = 'Matt Stec'
REQUIRES_PYTHON = '>=3.5'

# What packages are required for this module to be executed?
REQUIRED = [
    'Jinja2>=2.9.0,<3',
    'requests>=2.9.0,<3',
    ]

# What packages are optional?
EXTRAS = {
    'pil-measurement': ['Pillow>=5,<6'],
    'dev': [
        'fonttools>=3.26', 'nox', 'Pillow>=5', 'pytest>=3.6', 'xmldiff>=2.4',
    ],
}

ENTRY_POINTS = """
               """

DOWNLOADS = [
]


# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier!

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
        LONG_DESCRIPTION = '\n' + f.read()
except Exception:
    LONG_DESCRIPTION = DESCRIPTION

# Load the package's version.py module as a dictionary.
ABOUT = {}
VERSION = None
VFILE = os.path.join(HERE, NAME, 'version.py')
if not VERSION:
    if os.path.exists(os.path.join(HERE, 'version.py')):
        copyfile(os.path.join(HERE, 'version.py'), VFILE)

    if not os.path.exists(VFILE):
        with open(VFILE, 'wt') as f:
            i = datetime.now()
            f.write('__version__ = "2.3.0-beta+{}{:0>2}{:0>2}.{}{:0>2}"'.format(i.year, i.month, i.day, i.hour, i.minute))
    with open(VFILE) as f:
        exec(f.read(), ABOUT)
else:
    ABOUT['__version__'] = VERSION


class DownloadS3(sdist.sdist):
    """ Download files from S3 for package inclusion """

    def run(self):
        import boto3
        resource = boto3.resource('s3')

        # Download JSON listing of releases
        release_obj = resource.Object('dsml-configuration', 'package-binaries/releases.json').get()
        release_contents = release_obj['Body'].read()
        release_data = json.loads(release_contents)

        for download in DOWNLOADS:
            local_file = os.path.join(HERE, download['target'])
            print('Downloading {}'.format(local_file))
            try:
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
            except TypeError:
                try:
                    os.makedirs(os.path.dirname(local_file))
                except OSError:
                    pass
            dl_key = release_data['releases'][download['release_key']]
            resource.Bucket('dsml-configuration').download_file(dl_key, local_file)
            compression = download.get('compression', None)
            if compression == 'tgz':
                tar = tarfile.open(local_file, 'r:gz')
                tar.extractall(os.path.dirname(local_file))
                tar.close()
            elif compression is None:
                pass
            else:
                raise NotImplementedError('Compression format not handled')
        sdist.sdist.run(self)
        os.unlink(VFILE)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(outs):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(outs))

    def initialize_options(self):
        """ Empty function """

    def finalize_options(self):
        """ Empty function """

    def run(self):
        """ Run the upload command """
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(HERE, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload -r dev dist/*')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=ABOUT['__version__'],
    author='Brian Quinlan + ' + AUTHOR,
    author_email='brian@sweetapp.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        ],
    description=DESCRIPTION,
    keywords='github gh-badges badge shield status',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    python_requires=REQUIRES_PYTHON,
    url='https://github.com/google/pybadges',
    packages=find_packages(exclude=('tests',)),
    package_data={
        'pybadges': [
            'badge-template-full.svg', 'default-widths.json', 'py.typed',
        ],
    },
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],
    entry_points=ENTRY_POINTS,
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='Proprietary',
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
        'sdist': DownloadS3,
    },
)
