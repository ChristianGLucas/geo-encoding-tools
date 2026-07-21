from gen.messages_pb2 import MGRSCoordinate
from nodes.mgrs_to_lat_lon import mgrs_to_lat_lon
from nodes.testkit import ax


def test_mgrs_to_lat_lon_known_landmark_cn_tower():
    # Independent oracle: the same CN Tower MGRS string derived (and
    # verified) in the LatLonToMGRS oracle test, decoded back.
    result = mgrs_to_lat_lon(ax(), MGRSCoordinate(mgrs="17TPJ3008433438"))
    assert result.error == ""
    expected_lat = 43 + 38 / 60 + 33.24 / 3600
    expected_lon = -(79 + 23 / 60 + 13.7 / 3600)
    assert abs(result.lat - expected_lat) < 1e-3
    assert abs(result.lon - expected_lon) < 1e-3


def test_mgrs_to_lat_lon_round_trips_lat_lon_to_mgrs():
    from nodes.lat_lon_to_mgrs import lat_lon_to_mgrs
    from gen.messages_pb2 import MGRSEncodeInput

    forward = lat_lon_to_mgrs(ax(), MGRSEncodeInput(lat=35.6586, lon=139.7454, precision=5))
    back = mgrs_to_lat_lon(ax(), MGRSCoordinate(mgrs=forward.mgrs))
    assert abs(back.lat - 35.6586) < 1e-4
    assert abs(back.lon - 139.7454) < 1e-4


def test_mgrs_to_lat_lon_empty_is_structured_error():
    result = mgrs_to_lat_lon(ax(), MGRSCoordinate(mgrs=""))
    assert result.error == "EMPTY_MGRS"


def test_mgrs_to_lat_lon_malformed_is_structured_error_not_a_crash():
    result = mgrs_to_lat_lon(ax(), MGRSCoordinate(mgrs="NOTAREALMGRS!!"))
    assert result.error == "INVALID_MGRS"


def test_mgrs_to_lat_lon_oversized_input_is_structured_error():
    result = mgrs_to_lat_lon(ax(), MGRSCoordinate(mgrs="1" * 200))
    assert result.error == "INVALID_MGRS"
