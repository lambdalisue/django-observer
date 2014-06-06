#!/usr/bin/env python
#==============================================================================
# A generic django app test running script.
#
# Author:   Alisue <lambdaliuse@hashnote.net>
# License:  MIT license
#==============================================================================
import os
import sys
import optparse     # argparse is prefered but it require python 2.7 or higher

# You can defined the default test apps here
DEFAULT_TEST_APPS = (
    'observer',
)


def console_main(args=None):
    parser = optparse.OptionParser(usage="python runtest.py [options] <apps>")
    parser.add_option('-v', '--verbosity', default='1',
                      choices=('0', '1', '2', '3'),
                      help=("Verbosity level; 0=minimal output, 1=normal "
                            "output, 2=verbose output, 3=very verbose "
                            "output"))
    parser.add_option('-i', '--interactive', action='store_true')
    parser.add_option('-b', '--base-dir', default=None,
                      help=("The base directory of the code. Used for "
                            "python 3 compiled codes."))
    opts, apps = parser.parse_args(args)

    if len(apps) == 0:
        apps = DEFAULT_TEST_APPS

    run_tests(apps,
              verbosity=int(opts.verbosity),
              interactive=opts.interactive,
              base_dir=opts.base_dir)


def run_tests(app_tests, verbosity=1, interactive=False, base_dir=None):
    base_dir = base_dir or os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(base_dir, 'src'))
    sys.path.insert(0, os.path.join(base_dir, 'tests'))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from django.conf import settings
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity,
                             interactive=interactive, failfast=False)
    failures = test_runner.run_tests(app_tests)
    sys.exit(bool(failures))


if __name__ == '__main__':
    console_main()

