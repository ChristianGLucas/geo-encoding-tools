import pygeohash as pgh

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import EncodedGeohash, GeohashEncodeInput
from nodes._common import GeoEncodingError, validate_geohash_precision, validate_point


def geohash_encode(ax: AxiomContext, input: GeohashEncodeInput) -> EncodedGeohash:
    """Encode a lat/lon point into a geohash string (base32, interleaved-bit
    encoding), via the pygeohash library. `precision` selects the string
    length: 1 character covers roughly a 5,000km cell, 12 characters is
    sub-millimeter; 0 or unset defaults to 9 (~4.8m).
    """
    try:
        validate_point(input.lat, input.lon)
        precision = validate_geohash_precision(input.precision)
        geohash = pgh.encode(input.lat, input.lon, precision=precision)
        return EncodedGeohash(geohash=geohash)
    except GeoEncodingError as e:
        return EncodedGeohash(error=e.token)
