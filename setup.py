import os
import sys

from setuptools import setup, find_packages

from training_rg.__version__ import (__title__, __description__, __version__, __author__,
                                     __author_email__, __url__, __license__)

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(f"""
==========================
Unsupported Python version
==========================

This version of {__title__} requires Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}, but you're trying to
install it on Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.

This may be because you are using a version of pip that doesn't
understand the python_requires classifier. Make sure you
have pip >= 9.0 and setuptools >= 24.2, then try again:

    $ python -m pip install --upgrade pip setuptools
    $ python -m pip install training-rg
""")
    sys.exit(1)


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        file = open(path, encoding='utf-8')
    except TypeError:
        file = open(path)
    return file.read()


def get_install_requires():
    return [i.strip() for i in open('requirements.txt').readlines()]


setup(
    name=__title__,
    description=__description__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    keywords=['python'],
    platforms=['Linux', 'Windows', 'MacOS'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'trg-seq=training_rg.sequential:main',
        ]
    },
    include_package_data=True,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    install_requires=get_install_requires(),
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Topic :: Education :: Testing',
        'Topic :: Games/Entertainment',
        'Topic :: Other/Nonlisted Topic',
    ],
)
