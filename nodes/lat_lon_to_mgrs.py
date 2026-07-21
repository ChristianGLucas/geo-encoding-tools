import mgrs as mgrslib

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import MGRSCoordinate, MGRSEncodeInput
from nodes._common import GeoEncodingError, validate_mgrs_precision, validate_point

_MGRS = mgrslib.MGRS()


def lat_lon_to_mgrs(ax: AxiomContext, input: MGRSEncodeInput) -> MGRSCoordinate:
    """Convert a lat/lon point to an MGRS (military grid) string, via
    hobuinc/mgrs, wrapping NGA's public-domain GEOTRANS. Unlike UTM, MGRS
    covers the poles too (via UPS internally), so no latitude-band
    restriction applies here. `precision` sets the digit count per
    easting/northing component, 0 (100km grid square) through 5 (1m).
    """
    try:
        validate_point(input.lat, input.lon)
        validate_mgrs_precision(input.precision)
        mgrs_str = _MGRS.toMGRS(input.lat, input.lon, MGRSPrecision=input.precision)
    except GeoEncodingError as e:
        return MGRSCoordinate(error=e.token)
    except mgrslib.core.MGRSError:
        return MGRSCoordinate(error="OUT_OF_RANGE")

    return MGRSCoordinate(mgrs=mgrs_str)
