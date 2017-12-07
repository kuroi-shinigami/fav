import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

testmodules = [x.split('.py').pop(0) for x in os.listdir(os.path.join(os.path.dirname(__file__))) if
               (x.startswith('test') and x.endswith('.py'))]

suite = unittest.TestSuite()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)
