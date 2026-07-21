from gen.messages_pb2 import EncodedGeohash, GeohashEncodeInput
from nodes.geohash_encode import geohash_encode
from nodes.testkit import ax


def test_encode_known_wikipedia_example():
    # Independent oracle: the worked example on Wikipedia's Geohash article
    # (https://en.wikipedia.org/wiki/Geohash) states that encoding
    # (42.6, -5.6) at 5 characters of precision produces "ezs42" -- a value
    # published independently of this package or of pygeohash's own tests.
    result = geohash_encode(ax(), GeohashEncodeInput(lat=42.6, lon=-5.6, precision=5))
    assert result.error == ""
    assert result.geohash == "ezs42"


def test_encode_default_precision_is_nine():
    result = geohash_encode(ax(), GeohashEncodeInput(lat=40.7484, lon=-73.9857))
    assert result.error == ""
    assert len(result.geohash) == 9
    assert result.geohash == "dr5ru6j28"


def test_encode_precision_one_is_a_single_char():
    result = geohash_encode(ax(), GeohashEncodeInput(lat=0.0, lon=0.0, precision=1))
    assert result.error == ""
    assert result.geohash == "s"


def test_encode_invalid_latitude_is_structured_error():
    result = geohash_encode(ax(), GeohashEncodeInput(lat=91.0, lon=0.0, precision=5))
    assert result.error == "INVALID_LAT"
    assert result.geohash == ""


def test_encode_invalid_longitude_is_structured_error():
    result = geohash_encode(ax(), GeohashEncodeInput(lat=0.0, lon=-181.0, precision=5))
    assert result.error == "INVALID_LON"
    assert result.geohash == ""


def test_encode_invalid_precision_is_structured_error():
    result = geohash_encode(ax(), GeohashEncodeInput(lat=0.0, lon=0.0, precision=13))
    assert result.error == "INVALID_PRECISION"
    assert result.geohash == ""


def test_encode_is_deterministic():
    a = geohash_encode(ax(), GeohashEncodeInput(lat=51.5074, lon=-0.1278, precision=8))
    b = geohash_encode(ax(), GeohashEncodeInput(lat=51.5074, lon=-0.1278, precision=8))
    assert a.geohash == b.geohash != ""
