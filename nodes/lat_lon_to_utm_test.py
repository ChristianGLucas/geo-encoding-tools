from gen.messages_pb2 import GeoCoordinate
from nodes.lat_lon_to_utm import lat_lon_to_utm
from nodes.testkit import ax


def test_utm_known_landmark_cn_tower():
    # Independent oracle: Wikipedia's "Military Grid Reference System"
    # article gives the CN Tower's UTM position as "17N 630084 4833438" for
    # its published coordinates 43deg38'33.24"N 79deg23'13.7"W -- a value
    # documented independently of this package or of the utm library's own
    # tests/docs.
    lat = 43 + 38 / 60 + 33.24 / 3600
    lon = -(79 + 23 / 60 + 13.7 / 3600)
    result = lat_lon_to_utm(ax(), GeoCoordinate(lat=lat, lon=lon))
    assert result.error == ""
    assert result.zone_number == 17
    assert result.hemisphere == "N"
    assert abs(result.easting - 630084) < 1.0
    assert abs(result.northing - 4833438) < 1.0


def test_utm_southern_hemisphere():
    # Sydney Opera House, southern hemisphere: hemisphere must resolve to S.
    result = lat_lon_to_utm(ax(), GeoCoordinate(lat=-33.8568, lon=151.2153))
    assert result.error == ""
    assert result.zone_number == 56
    assert result.hemisphere == "S"


def test_utm_invalid_latitude():
    result = lat_lon_to_utm(ax(), GeoCoordinate(lat=91.0, lon=0.0))
    assert result.error == "INVALID_LAT"


def test_utm_latitude_outside_utm_band_is_out_of_range():
    # UTM (unlike MGRS) is undefined above 84N / below 80S -- Antarctica's
    # interior, for instance.
    result = lat_lon_to_utm(ax(), GeoCoordinate(lat=-85.0, lon=0.0))
    assert result.error == "OUT_OF_RANGE"


def test_utm_is_deterministic():
    a = lat_lon_to_utm(ax(), GeoCoordinate(lat=48.8584, lon=2.2945))
    b = lat_lon_to_utm(ax(), GeoCoordinate(lat=48.8584, lon=2.2945))
    assert a.easting == b.easting and a.northing == b.northing
