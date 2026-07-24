import json

from gen.messages_pb2 import GeohashCell, GeohashEncodeInput
from nodes.geohash_decode import geohash_decode
from nodes.geohash_encode import geohash_encode
from nodes.testkit import ax


def test_decode_known_wikipedia_example():
    # Independent oracle, same source as the encode test: Wikipedia's
    # Geohash article states "ezs42" decodes to the interval
    # lat [42.583, 42.627], lon [-5.625, -5.581], center (42.605, -5.603).
    result = geohash_decode(ax(), GeohashCell(geohash="ezs42"))
    assert result.error == ""
    assert result.lat == 42.60498046875
    assert result.lon == -5.60302734375
    assert abs(result.min_lat - 42.583) < 0.001
    assert abs(result.max_lat - 42.627) < 0.001
    assert abs(result.min_lon - (-5.625)) < 0.001
    assert abs(result.max_lon - (-5.581)) < 0.001


def test_decode_error_margins_match_bbox_half_width():
    result = geohash_decode(ax(), GeohashCell(geohash="u4pruyd"))
    assert result.error == ""
    assert abs((result.max_lat - result.min_lat) / 2 - result.lat_error) < 1e-9
    assert abs((result.max_lon - result.min_lon) / 2 - result.lon_error) < 1e-9


def test_decode_geojson_is_a_valid_polygon_matching_the_bbox():
    result = geohash_decode(ax(), GeohashCell(geohash="u4pruyd"))
    geom = json.loads(result.geojson)
    assert geom["type"] == "Polygon"
    ring = geom["coordinates"][0]
    assert ring[0] == ring[-1]  # closed ring
    lons = [pt[0] for pt in ring]
    lats = [pt[1] for pt in ring]
    assert min(lons) == result.min_lon
    assert max(lons) == result.max_lon
    assert min(lats) == result.min_lat
    assert max(lats) == result.max_lat


def test_decode_round_trips_encode():
    encoded = geohash_encode(ax(), GeohashEncodeInput(lat=40.7484, lon=-73.9857, precision=9))
    decoded = geohash_decode(ax(), GeohashCell(geohash=encoded.geohash))
    assert abs(decoded.lat - 40.7484) < 1e-4
    assert abs(decoded.lon - (-73.9857)) < 1e-4


def test_decode_empty_geohash_is_structured_error():
    result = geohash_decode(ax(), GeohashCell(geohash=""))
    assert result.error == "EMPTY_GEOHASH"


def test_decode_invalid_character_is_structured_error():
    # 'a', 'i', 'l', 'o' are never valid geohash base32 characters.
    result = geohash_decode(ax(), GeohashCell(geohash="abcio"))
    assert result.error == "INVALID_GEOHASH"


def test_decode_large_input_does_not_crash():
    # No length cap is imposed by this node -- the platform bounds payload
    # size, not this node. A long but charset-valid geohash decodes to a
    # degenerate (extremely small error-margin) point rather than crashing;
    # pygeohash's own bisection algorithm handles arbitrary precision.
    result = geohash_decode(ax(), GeohashCell(geohash="0" * 100))
    assert result.error == ""
    assert result.lat == -90.0
    assert result.lon == -180.0
