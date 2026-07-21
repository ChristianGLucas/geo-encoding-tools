from gen.axiom_context import AxiomContext
from gen.messages_pb2 import GeohashPair, GeohashRelation
from nodes._common import GEOHASH_ALPHABET, GeoEncodingError, validate_geohash_string


def geohash_compare(ax: AxiomContext, input: GeohashPair) -> GeohashRelation:
    """Compare two geohashes: whether `geohash_a` spatially contains
    `geohash_b`, and their longest common prefix. For geohashes, spatial
    containment IS the prefix relationship: every finer cell nested inside a
    coarser one shares that coarser cell's full character prefix, by
    construction of the interleaved-bit encoding -- so `a_contains_b` is true
    exactly when `geohash_a` is a prefix of (no longer than, and matching)
    `geohash_b`. This is pure string comparison; no coordinate math.
    """
    try:
        a = validate_geohash_string(input.geohash_a)
        b = validate_geohash_string(input.geohash_b)
    except GeoEncodingError as e:
        return GeohashRelation(error=e.token)

    if any(c not in GEOHASH_ALPHABET for c in a) or any(c not in GEOHASH_ALPHABET for c in b):
        return GeohashRelation(error="INVALID_GEOHASH")

    prefix_len = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        prefix_len += 1
    common_prefix = a[:prefix_len]
    a_contains_b = len(a) <= len(b) and common_prefix == a

    return GeohashRelation(
        a_contains_b=a_contains_b,
        common_prefix=common_prefix,
        common_prefix_length=prefix_len,
    )
