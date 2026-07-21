from gen.messages_pb2 import GeohashPair
from nodes.geohash_compare import geohash_compare
from nodes.testkit import ax


def test_compare_prefix_means_containment():
    # "u4pruy" is exactly the first 6 characters of "u4pruyd" -- by the
    # definition of the geohash encoding (each added character subdivides
    # the parent cell), the shorter hash's cell strictly contains the
    # longer hash's cell.
    result = geohash_compare(ax(), GeohashPair(geohash_a="u4pruy", geohash_b="u4pruyd"))
    assert result.error == ""
    assert result.a_contains_b is True
    assert result.common_prefix == "u4pruy"
    assert result.common_prefix_length == 6


def test_compare_is_not_symmetric():
    # Swapping a/b: the now-longer geohash cannot contain the shorter one,
    # even though they still share the same prefix.
    result = geohash_compare(ax(), GeohashPair(geohash_a="u4pruyd", geohash_b="u4pruy"))
    assert result.error == ""
    assert result.a_contains_b is False
    assert result.common_prefix == "u4pruy"
    assert result.common_prefix_length == 6


def test_compare_equal_hashes_contain_each_other():
    result = geohash_compare(ax(), GeohashPair(geohash_a="dr5ru6j28", geohash_b="dr5ru6j28"))
    assert result.a_contains_b is True
    assert result.common_prefix == "dr5ru6j28"
    assert result.common_prefix_length == 9


def test_compare_disjoint_hashes_share_no_prefix():
    # Antipodal-ish cells (different first character) share nothing.
    result = geohash_compare(ax(), GeohashPair(geohash_a="ezs42", geohash_b="9q8yy"))
    assert result.a_contains_b is False
    assert result.common_prefix == ""
    assert result.common_prefix_length == 0


def test_compare_case_insensitive():
    result = geohash_compare(ax(), GeohashPair(geohash_a="U4PRUY", geohash_b="u4pruyd"))
    assert result.a_contains_b is True
    assert result.common_prefix == "u4pruy"


def test_compare_empty_input_is_structured_error():
    result = geohash_compare(ax(), GeohashPair(geohash_a="", geohash_b="u4pruy"))
    assert result.error == "EMPTY_GEOHASH"


def test_compare_invalid_character_is_structured_error():
    result = geohash_compare(ax(), GeohashPair(geohash_a="u4pruy", geohash_b="u4pra0i"))
    assert result.error == "INVALID_GEOHASH"
