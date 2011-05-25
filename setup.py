from distutils.core import setup


setup(name='gomoku',
      version='0.1',
      packages=['gomoku'],
      scripts=['bin/gomoku-server.py', 'bin/gomoku-client-cli.py']
      )
