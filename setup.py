#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('pychrome/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


requirements = [
    'click>=6.0',
    'websocket-client>=0.44.0',
    'requests>=2.13.0',
]

setup(
    name='pychrome',
    version=version,
    description="A Python Package for the Google Chrome Dev Protocol",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="fate0",
    author_email='fate0@fatezero.org',
    url='https://github.com/fate0/pychrome',
    packages=find_packages(),
    package_dir={},
    entry_points={
        'console_scripts': [
            'pychrome=pychrome.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='pychrome',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Browsers'
    ],
)

