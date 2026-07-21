from gen.messages_pb2 import UTMCoordinate
from nodes.utm_to_mgrs import utm_to_mgrs
from nodes.testkit import ax


def test_utm_to_mgrs_known_pair():
    # Independent oracle: Wikipedia's Universal Transverse Mercator article
    # states the UTM coordinate "31 N 303760 5787415" is equivalent to the
    # MGRS grid reference "31U CT 03760 87415" -- documented independently
    # of this package, and not derived by going through a lat/lon round trip.
    result = utm_to_mgrs(ax(), UTMCoordinate(zone_number=31, hemisphere="N", easting=303760, northing=5787415))
    assert result.error == ""
    assert result.mgrs == "31UCT0376087415"


def test_utm_to_mgrs_invalid_zone():
    result = utm_to_mgrs(ax(), UTMCoordinate(zone_number=0, hemisphere="N", easting=500000, northing=0))
    assert result.error == "INVALID_UTM_ZONE"


def test_utm_to_mgrs_invalid_hemisphere():
    result = utm_to_mgrs(ax(), UTMCoordinate(zone_number=31, hemisphere="E", easting=303760, northing=5787415))
    assert result.error == "INVALID_HEMISPHERE"
