from gen.messages_pb2 import MGRSCoordinate
from nodes.mgrs_to_utm import mgrs_to_utm
from nodes.testkit import ax


def test_mgrs_to_utm_known_pair():
    # Independent oracle: the same Wikipedia UTM<->MGRS equivalence used in
    # the UtmToMgrs oracle test, in reverse: "31U CT 03760 87415" <-> "31 N
    # 303760 5787415".
    result = mgrs_to_utm(ax(), MGRSCoordinate(mgrs="31UCT0376087415"))
    assert result.error == ""
    assert result.zone_number == 31
    assert result.hemisphere == "N"
    assert abs(result.easting - 303760) < 1.0
    assert abs(result.northing - 5787415) < 1.0


def test_mgrs_to_utm_round_trips_utm_to_mgrs():
    from nodes.utm_to_mgrs import utm_to_mgrs
    from gen.messages_pb2 import UTMCoordinate

    forward = utm_to_mgrs(ax(), UTMCoordinate(zone_number=18, hemisphere="N", easting=585628, northing=4511322))
    back = mgrs_to_utm(ax(), MGRSCoordinate(mgrs=forward.mgrs))
    assert back.zone_number == 18
    assert back.hemisphere == "N"
    assert abs(back.easting - 585628) < 1.0
    assert abs(back.northing - 4511322) < 1.0


def test_mgrs_to_utm_empty_is_structured_error():
    result = mgrs_to_utm(ax(), MGRSCoordinate(mgrs=""))
    assert result.error == "EMPTY_MGRS"


def test_mgrs_to_utm_malformed_is_structured_error_not_a_crash():
    result = mgrs_to_utm(ax(), MGRSCoordinate(mgrs="!!!GARBAGE!!!"))
    assert result.error == "INVALID_MGRS"
