import unittest
from unittest import TestCase
from quadkey.util import *


class UtilTest(TestCase):

    def testPrecondition(self):
        self.assertTrue(self.pre(True))
        with self.assertRaises(AssertionError):
            self.pre(False)

    def testPostcondition(self):
        pass

    @precondition(lambda c, x: x is True)
    def pre(self, x):
        return x
