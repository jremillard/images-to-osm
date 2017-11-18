from __future__ import division

try:
    xrange
except NameError:
    xrange = range

from QuadKey.quadkey.util import precondition
from QuadKey.quadkey.tile_system import TileSystem, valid_key

LAT_STR = 'lat'
LON_STR = 'lon'

class QuadKey:

    @precondition(lambda c, key: valid_key(key))
    def __init__(self, key):
        """
        A quadkey must be between 1 and 23 digits and can only contain digit[0-3]
        """
        self.key = key
        self.level = len(key)

    def children(self):
        if self.level >= 23:
            return []
        return [QuadKey(self.key + str(k)) for k in [0, 1, 2, 3]]

    def parent(self):
        return QuadKey(self.key[:-1])

    def nearby(self):
        tile, level = TileSystem.quadkey_to_tile(self.key)
        perms = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                 (0, 1), (1, -1), (1, 0), (1, 1)]
        tiles = set(
            map(lambda perm: (abs(tile[0] + perm[0]), abs(tile[1] + perm[1])), perms))
        return [TileSystem.tile_to_quadkey(tile, level) for tile in tiles]

    def is_ancestor(self, node):
        """
                If node is ancestor of self
                Get the difference in level
                If not, None
        """
        if self.level <= node.level or self.key[:len(node.key)] != node.key:
            return None
        return self.level - node.level

    def is_descendent(self, node):
        """
                If node is descendent of self
                Get the difference in level
                If not, None
        """
        return node.is_ancestor(self)

    def area(self):
        size = TileSystem.map_size(self.level)
        LAT = 0
        res = TileSystem.ground_resolution(LAT, self.level)
        side = (size / 2) * res
        return side * side

    def xdifference(self, to):
        """ Generator
            Gives the difference of quadkeys between self and to
            Generator in case done on a low level
            Only works with quadkeys of same level
        """
        x,y = 0,1
        assert self.level == to.level
        self_tile = list(self.to_tile()[0])
        to_tile = list(to.to_tile()[0])
        if self_tile[x] >= to_tile[x] and self_tile[y] <= self_tile[y]:
            ne_tile, sw_tile = self_tile, to_tile
        else:
            sw_tile, ne_tile = self_tile, to_tile
        cur = ne_tile[:]
        while cur[x] >= sw_tile[x]:
            while cur[y] <= sw_tile[y]:
                yield from_tile(tuple(cur), self.level)
                cur[y] += 1
            cur[x] -= 1
            cur[y] = ne_tile[y]

    def difference(self, to):
        """ Non generator version of xdifference
        """
        return [qk for qk in self.xdifference(to)]

    def unwind(self):
        """ Get a list of all ancestors in descending order of level, including a new instance  of self
        """
        return [ QuadKey(self.key[:l+1]) for l in reversed(range(len(self.key))) ]

    def to_tile(self):
        return TileSystem.quadkey_to_tile(self.key)

    def to_geo(self, centered=False):
        ret = TileSystem.quadkey_to_tile(self.key)
        tile = ret[0]
        lvl = ret[1]
        pixel = TileSystem.tile_to_pixel(tile, centered)
        return TileSystem.pixel_to_geo(pixel, lvl)

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.key

    def __repr__(self):
        return self.key

def from_geo(geo, level):
    """
    Constucts a quadkey representation from geo and level
    geo => (lat, lon)
    If lat or lon are outside of bounds, they will be clipped
    If level is outside of bounds, an AssertionError is raised

    """
    pixel = TileSystem.geo_to_pixel(geo, level)
    tile = TileSystem.pixel_to_tile(pixel)
    key = TileSystem.tile_to_quadkey(tile, level)
    return QuadKey(key)

def from_tile(tile, level):
    return QuadKey(TileSystem.tile_to_quadkey(tile, level))

def from_str(qk_str):
    return QuadKey(qk_str)

def geo_to_dict(geo):
    """ Take a geo tuple and return a labeled dict
        (lat, lon) -> {'lat': lat, 'lon', lon}
    """
    return {LAT_STR: geo[0], LON_STR: geo[1]}

