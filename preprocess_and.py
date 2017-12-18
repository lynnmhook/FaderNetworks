import subprocess
import os
import importlib

os.chdir('data')

import data.preprocess

os.chdir('..')

module = sys.argv[1]
sys.argv = sys.argv[2:]

importlib.import_module(module)
