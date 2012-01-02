#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:       Alisue
# Last Change:  18-Mar-2011.
#
from setuptools import setup, find_packages

version = "0.3rc2"

def read(filename):
    import os.path
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name="django-observer",
    version=version,
    description = "Watch any object/field/relation/generic relation of django and recive signals",
    long_description=read('README.rst'),
    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = "django signals object field relation generic",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    url=r"https://github.com/lambdalisue/django-observer",
    download_url = r"https://github.com/lambdalisue/django-observer/tarball/master",
    license = 'BSD',
    packages = find_packages(),
    include_package_data = False,
    zip_safe = True,
    install_requires=[
        'setuptools',
        'django>=1.2',
        ],
)
