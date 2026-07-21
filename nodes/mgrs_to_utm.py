import mgrs as mgrslib

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import MGRSCoordinate, UTMCoordinate
from nodes._common import GeoEncodingError, validate_mgrs_string

_MGRS = mgrslib.MGRS()


def mgrs_to_utm(ax: AxiomContext, input: MGRSCoordinate) -> UTMCoordinate:
    """Convert an MGRS string directly to its UTM coordinate, via
    hobuinc/mgrs wrapping NGA's public-domain GEOTRANS -- no lat/lon
    round-trip.
    """
    try:
        mgrs_str = validate_mgrs_string(input.mgrs)
        zone, hemisphere, easting, northing = _MGRS.MGRSToUTM(mgrs_str)
    except GeoEncodingError as e:
        return UTMCoordinate(error=e.token)
    except mgrslib.core.MGRSError:
        return UTMCoordinate(error="INVALID_MGRS")

    return UTMCoordinate(
        zone_number=zone,
        hemisphere=hemisphere,
        easting=easting,
        northing=northing,
    )
