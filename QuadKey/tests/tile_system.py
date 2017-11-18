import unittest
from unittest import TestCase
from quadkey.tile_system import TileSystem


class TileSystemTest(TestCase):

    def testClip(self):
        self.assertEqual(1, TileSystem.clip(0, (1, 5)))
        self.assertEqual(5, TileSystem.clip(10, (1, 5)))
        self.assertEqual(3, TileSystem.clip(3, (1, 5)))
        with self.assertRaises(AssertionError):
            TileSystem.clip(7, (5, 1))

    def testMapSize(self):
        self.assertEqual(512, TileSystem.map_size(1))
        with self.assertRaises(AssertionError):
            TileSystem.map_size(0)

    def testGroundResolution(self):
        geo = (40., -105.)
        res = 936.86657226219847
        TileSystem.ground_resolution(geo[0], 7)

    def testMapScale(self):
        geo = (40., -105.)
        level = 7
        dpi = 96
        scale = 3540913.029022482 # 3540913.0290224836 ??
        self.assertEqual(scale, TileSystem.map_scale(geo[0], level, dpi))

    def testGeoToPixel(self):
        geo = (40., -105.)
        level = 7
        pixel = (6827, 12405)
        self.assertEqual(pixel, TileSystem.geo_to_pixel(geo, level))

    def testPixelToGeo(self):
        pixel = (6827, 12405)
        level = 7
        geo = (40.002372, -104.996338)
        self.assertEqual(geo, TileSystem.pixel_to_geo(pixel, level))

    def testPixelToTile(self):
        pixel = (6827, 12405)
        tile = (26, 48)
        self.assertEqual(tile, TileSystem.pixel_to_tile(pixel))

    def testTileToPixel(self):
        tile = (26, 48)
        pixel = (6656, 12288)
        self.assertEqual(pixel, TileSystem.tile_to_pixel(tile))

    def testTileToQuadkey(self):
        tile = (26, 48)
        level = 7
        key = "0231010"
        self.assertEqual(key, TileSystem.tile_to_quadkey(tile, level))

    def testQuadkeyToTile(self):
        tile = (26, 48)
        level = 7
        key = "0231010"
        self.assertEqual([tile, level], TileSystem.quadkey_to_tile(key))
