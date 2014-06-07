import os
import sys
from setuptools import setup, find_packages, Command

NAME = 'django-observer'
VERSION = '0.4.3'


class compile_docs(Command):
    description = ("re-compile documentations")
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        compile_docs.update_docs()
        compile_docs.compile_docs()

    @classmethod
    def update_docs(cls):
        """
        Update docs via sphinx-apidoc (src -> docs)
        """
        os.system('sphinx-docs -o docs src -f')
        return True

    @classmethod
    def compile_docs(cls):
        """
        Compile '.rst' files into '.html' files via Sphinx.
        """
        original_cwd = os.getcwd()
        BASE = os.path.abspath(os.path.dirname(__file__))
        root = os.path.join(BASE, 'docs')
        os.chdir(root)
        os.system('make html')
        os.system('xdg-open _build/html/index.html')
        os.chdir(original_cwd)
        return True


def read(filename):
    BASE_DIR = os.path.dirname(__file__)
    filename = os.path.join(BASE_DIR, filename)
    with open(filename, 'r') as fi:
        return fi.read()


def readlist(filename):
    rows = read(filename).split("\n")
    rows = [x.strip() for x in rows if x.strip()]
    return list(rows)

# if we are running on python 3, enable 2to3 and
# let it use the custom fixers from the custom_fixers
# package.
extra = {}
if sys.version_info >= (3, 0):
    extra.update(
        use_2to3=True,
    )

setup(
    name=NAME,
    version=VERSION,
    description=("Watch any object/field/relation/generic relation of django "
                 "and call the callback when the watched object is modified"),
    long_description = read('README.rst'),
    classifiers = (
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    keywords = "django app registration inspection",
    author = 'Alisue',
    author_email = 'lambdalisue@hashnote.net',
    url = 'https://github.com/lambdalisue/%s' % NAME,
    download_url = 'https://github.com/lambdalisue/%s/tarball/master' % NAME,
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    package_data = {
        '': ['README.rst',
             'requirements.txt',
             'requirements-test.txt',
             'requirements-docs.txt'],
    },
    zip_safe=True,
    install_requires=readlist('requirements.txt'),
    test_suite='runtests.run_tests',
    tests_require=readlist('requirements-test.txt'),
    cmdclass={
        'compile_docs': compile_docs,
    },
    **extra
)
