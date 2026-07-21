import mgrs as mgrslib

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import MGRSCoordinate, UTMCoordinate
from nodes._common import MAX_MGRS_PRECISION, GeoEncodingError, validate_utm

_MGRS = mgrslib.MGRS()


def utm_to_mgrs(ax: AxiomContext, input: UTMCoordinate) -> MGRSCoordinate:
    """Convert a UTM coordinate directly to an MGRS string, via hobuinc/mgrs
    wrapping NGA's public-domain GEOTRANS -- no lat/lon round-trip. Always
    encodes at full (5, 1m) precision: UTMCoordinate carries a full-precision
    easting/northing with no separate "how many digits" concept of its own to
    forward.
    """
    try:
        validate_utm(input.zone_number, input.hemisphere)
        mgrs_str = _MGRS.UTMToMGRS(
            input.zone_number,
            input.hemisphere,
            input.easting,
            input.northing,
            MGRSPrecision=MAX_MGRS_PRECISION,
        )
    except GeoEncodingError as e:
        return MGRSCoordinate(error=e.token)
    except mgrslib.core.MGRSError:
        return MGRSCoordinate(error="OUT_OF_RANGE")

    return MGRSCoordinate(mgrs=mgrs_str)
