import sys
import os
testdir = os.path.dirname(__file__)
srcdir = '../bot'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
for p in sys.path:
    print(p)
