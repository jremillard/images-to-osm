from __future__ import division

try:
    xrange
except NameError:
    xrange = range

import unittest
from unittest import TestCase
import quadkey

class QuadkeyTest(TestCase):

    def testInit(self):
        qk = quadkey.from_str('0321201120')
        with self.assertRaises(AssertionError):
            qk = quadkey.from_str('')
        with self.assertRaises(AssertionError):
            qk = quadkey.from_str('0156510012')

    def testFromGeo(self):
        geo = (40, -105)
        level = 7
        key = quadkey.from_str('0231010')
        self.assertEqual(key, quadkey.from_geo(geo, level))

    def testEquality(self):
        one = quadkey.from_str('00')
        two = quadkey.from_str('00')
        self.assertEqual(one, two)
        three = quadkey.from_str('0')
        self.assertNotEqual(one, three)

    def testChildren(self):
        qk = quadkey.from_str('0')
        self.assertEqual(
            [c.key for c in qk.children()], ['00', '01', '02', '03'])
        qk = quadkey.from_str(''.join(['0' for x in xrange(23)]))
        self.assertEqual(qk.children(), [])

    def testAncestry(self):
        one = quadkey.from_str('0')
        two = quadkey.from_str('0101')
        self.assertEqual(3, one.is_descendent(two))
        self.assertIsNone(two.is_descendent(one))
        self.assertEqual(3, two.is_ancestor(one))
        three = quadkey.from_str('1')
        self.assertIsNone(three.is_ancestor(one))

    def testNearby(self):
        qk = quadkey.from_str('0')
        self.assertEqual(set(['1', '2', '3']), set(qk.nearby()))
        #qk = quadkey.from_str('01')
        #self.assertEqual(
        #    set(['00', '10', '02', '03', '13', '33', '32', '23']), set(qk.nearby()))

    def testUnwind(self):
        qk = quadkey.from_str('0123')
        self.assertEqual(
                ['0123', '012', '01', '0'],
                [qk.key for qk in qk.unwind()]
        )

    def testDifference(self):
        _from = quadkey.from_str('0320101102')
        _to = quadkey.from_str('0320101110')
        diff = set(['0320101102','0320101100','0320101103', '0320101101', '0320101112', '0320101110'])
        self.assertEqual(diff, set([qk.key for qk in _to.difference(_from)]))
        self.assertEqual(diff, set([qk.key for qk in _from.difference(_to)]))



