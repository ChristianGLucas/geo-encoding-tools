from gen.messages_pb2 import UTMCoordinate
from nodes.utm_to_lat_lon import utm_to_lat_lon
from nodes.testkit import ax


def test_utm_to_lat_lon_known_landmark_cn_tower():
    # Independent oracle: Wikipedia's MGRS article publishes "17N 630084
    # 4833438" as the CN Tower's UTM position; the CN Tower's own published
    # coordinates are 43deg38'33.24"N 79deg23'13.7"W.
    result = utm_to_lat_lon(ax(), UTMCoordinate(zone_number=17, hemisphere="N", easting=630084, northing=4833438))
    assert result.error == ""
    expected_lat = 43 + 38 / 60 + 33.24 / 3600
    expected_lon = -(79 + 23 / 60 + 13.7 / 3600)
    assert abs(result.lat - expected_lat) < 1e-3
    assert abs(result.lon - expected_lon) < 1e-3


def test_utm_to_lat_lon_round_trips_lat_lon_to_utm():
    from nodes.lat_lon_to_utm import lat_lon_to_utm
    from gen.messages_pb2 import GeoCoordinate

    forward = lat_lon_to_utm(ax(), GeoCoordinate(lat=51.5074, lon=-0.1278))
    back = utm_to_lat_lon(ax(), UTMCoordinate(
        zone_number=forward.zone_number, hemisphere=forward.hemisphere,
        easting=forward.easting, northing=forward.northing,
    ))
    assert abs(back.lat - 51.5074) < 1e-5
    assert abs(back.lon - (-0.1278)) < 1e-5


def test_utm_to_lat_lon_invalid_zone():
    result = utm_to_lat_lon(ax(), UTMCoordinate(zone_number=61, hemisphere="N", easting=500000, northing=0))
    assert result.error == "INVALID_UTM_ZONE"


def test_utm_to_lat_lon_invalid_hemisphere():
    result = utm_to_lat_lon(ax(), UTMCoordinate(zone_number=17, hemisphere="X", easting=500000, northing=0))
    assert result.error == "INVALID_HEMISPHERE"


def test_utm_to_lat_lon_out_of_range_easting():
    result = utm_to_lat_lon(ax(), UTMCoordinate(zone_number=17, hemisphere="N", easting=1.0, northing=0.0))
    assert result.error == "OUT_OF_RANGE"
