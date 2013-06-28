#!/usr/bin/python

from optparse import OptionParser
import os
import re
import subprocess
import tempfile
import sys

ALL_SUITES = [ 
  'biz/unit-test',
  'cc-gui/test', 
  'chrome/unit-test',
  'cws/impl-unit-test',
  'fetch/unit-test',
  'frontier/shared-unit-test',
  'frontier/unit-test',
  'nabook/unit-test',
  'nmp/unit-test',
  'nprofile/unit-test',
  'nsettings/unit-test',
  'pulse/gui-unit-test',
  'reg/impl-unit-test' 
]
ANT = '/local/apache-ant-1.7.1/bin/ant'

def backup_files():
  return
  for suite in suites:
    results_file = os.path.join(os.getcwd(), suite, 'all_tests_results')
    if os.path.exists(results_file):
      os.rename(results_file, os.path.join(os.getcwd(), suite, 'all_tests_results.bak'))

def run_tests(suites, rebuild):
  error_re = re.compile('Errors: [^0]')
  failure_re = re.compile('Failures: [^0]')
  logfile = open(os.path.join(os.getcwd(), 'all_tests.log'), 'w')
  for suite in suites:
    print 'Running tests in %s' % suite
    build_file = os.path.join(os.getcwd(), suite, 'build.xml')
    args = [ ANT, '-f', build_file ]
    if not rebuild:
      print 'WARNING: NOT rebuilding for suite %s' % suite
      args.append('-Dno.full.build=true')
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.communicate()
    results_file = os.path.join(os.getcwd(), suite, 'all_tests_results')
    output_file = open(results_file, 'w')
    output_file.write(output[0])
    output_file.close()
    if error_re.search(output[0]):
      logfile.write('Errors in %s\n' % suite)
    if failure_re.search(output[0]):
      logfile.write('Failures in %s\n' % suite)
  logfile.close()


def main():
  usage = 'usage: %prog [options] suite1 suite2 ...'
  parser = OptionParser(usage=usage, description='Runs all unit tests for Frontier-dependent code.')
  parser.add_option('-l', '--list', help='List default list of suites',
                    dest='list', action='store_true', default=False)
  parser.add_option('-r', '--rebuild', help='Should rebuild all',
                    dest='rebuild', action='store_true', default=False)
  parser.add_option('-b', '--backup', help='Backup previous run files',
                    dest='backup', action='store_true', default=False)
  (options, suites) = parser.parse_args()

  lock_file_path = os.path.join(tempfile.gettempdir(), 'run_all_tests.lock')
  if os.path.exists(lock_file_path):
    raise Exception('Another instance of %s is running. Delete %s if '
        'you are sure this is not so' % (os.path.basename(sys.argv[0]), lock_file_path))
  
  try:
    open(os.path.join(tempfile.gettempdir(), 'run_all_tests.lock'), 'w').close()

    if options.list:
      print '\n'.join(ALL_SUITES)
      return
    if not suites:
      suites = ALL_SUITES
    
    # Touch the lock file
    if options.backup:
      backup_files()
    run_tests(suites, options.rebuild)
  finally:
    os.unlink(os.path.join(tempfile.gettempdir(), 'run_all_tests.lock'))


if __name__ == '__main__':
	main()

