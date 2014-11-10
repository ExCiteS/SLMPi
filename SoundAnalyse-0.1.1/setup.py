from distutils.core import setup, Extension

setup(name = "SoundAnalyse",
      version = "0.1.1",
      author = "Nathan Whitehead",
      author_email = "nwhitehe@gmail.com",
      url = "http://code.google.com/p/pygalaxy/",
      py_modules = ['analyse'],
      ext_modules = [Extension("analyseffi", ["analyseffi.c"])],
      description = "Analyse sound chunks for pitch and loudness",
      long_description = '''
This module provides functions to analyse sound chunks to detect
loudness and pitch.  It also includes some utility functions for
converting midi note numbers to and from frequencies.  Designed for
realtime microphone input for singing games.
''',
      )
