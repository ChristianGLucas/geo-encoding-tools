from gen.messages_pb2 import MGRSEncodeInput
from nodes.lat_lon_to_mgrs import lat_lon_to_mgrs
from nodes.testkit import ax


def test_mgrs_known_landmark_cn_tower():
    # Independent oracle: same CN Tower published position as the UTM tests
    # (43deg38'33.24"N 79deg23'13.7"W), converted through the MGRS grid-zone
    # convention (documented in the Wikipedia MGRS article's own worked
    # example format) rather than through this package's own UTM path.
    lat = 43 + 38 / 60 + 33.24 / 3600
    lon = -(79 + 23 / 60 + 13.7 / 3600)
    result = lat_lon_to_mgrs(ax(), MGRSEncodeInput(lat=lat, lon=lon, precision=5))
    assert result.error == ""
    assert result.mgrs == "17TPJ3008433438"


def test_mgrs_precision_zero_is_100km_square_only():
    result = lat_lon_to_mgrs(ax(), MGRSEncodeInput(lat=40.7484, lon=-73.9857, precision=0))
    assert result.error == ""
    assert result.mgrs == "18TWL"


def test_mgrs_precision_controls_digit_count():
    result = lat_lon_to_mgrs(ax(), MGRSEncodeInput(lat=40.7484, lon=-73.9857, precision=5))
    assert result.error == ""
    # grid-zone(3) + 100km-square(2) + 2*precision digits
    assert len(result.mgrs) == 5 + 2 * 5


def test_mgrs_invalid_precision():
    result = lat_lon_to_mgrs(ax(), MGRSEncodeInput(lat=0.0, lon=0.0, precision=6))
    assert result.error == "INVALID_PRECISION"


def test_mgrs_invalid_longitude():
    result = lat_lon_to_mgrs(ax(), MGRSEncodeInput(lat=0.0, lon=200.0, precision=5))
    assert result.error == "INVALID_LON"


def test_mgrs_covers_polar_region_where_utm_does_not():
    # 85N is outside UTM's -80..84 band but MGRS (via UPS) still resolves it.
    result = lat_lon_to_mgrs(ax(), MGRSEncodeInput(lat=85.0, lon=0.0, precision=5))
    assert result.error == ""
    assert result.mgrs != ""
