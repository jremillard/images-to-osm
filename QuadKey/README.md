QuadKey
=======

Quad key object used for Geospatial segmentation. Based off the idea of a quadtree and used as the Bing Maps tile system.

Given a (lat, lon) and level produce a quadkey to be used in Bing Maps.
Can also supply methods to generate a Google Maps TileXYZ

Built off of the TileSystem static class outlined here: http://msdn.microsoft.com/en-us/library/bb259689.aspx

Converts a lat,lon to pixel space to tile space to a quadkey 


    import quadkey

    qk = quadkey.from_geo((-105, 40), 17)
    print qk.key # => 02310101232121212 
    assert qk.level is 17
    tile = qk.to_tile() # => [(x, y), z]

Not a lot of documentation here, but the implementation has quite a bit, so look at the QuadKey definitions for better documention


Install
-------

The package on pypi is quadtweet, so the recommended installation is with pip

     pip install quadkey

Methods
-------

There are many straightforward methods, so I'll only go into detail of the unique ones

* children()
* parent()
* is_ancestor()
* is_descendent()
* area()
* to_geo()
* to_tile()

####difference(to)

Gets the quadkeys between self and to forming a rectangle, inclusive.

    qk.difference(to) -> [qk,,,,,to]

####unwind()

Gets a list of all ancestors in descending order by level, inclusive.

    QuadKey('0123').unwind() -> ['0123','012','01','0']
