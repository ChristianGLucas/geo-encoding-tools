import mgrs as mgrslib

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import GeoCoordinate, MGRSCoordinate
from nodes._common import GeoEncodingError, validate_mgrs_string

_MGRS = mgrslib.MGRS()


def mgrs_to_lat_lon(ax: AxiomContext, input: MGRSCoordinate) -> GeoCoordinate:
    """Convert an MGRS (military grid) string back to lat/lon, via
    hobuinc/mgrs, wrapping NGA's public-domain GEOTRANS.
    """
    try:
        mgrs_str = validate_mgrs_string(input.mgrs)
        lat, lon = _MGRS.toLatLon(mgrs_str)
    except GeoEncodingError as e:
        return GeoCoordinate(error=e.token)
    except mgrslib.core.MGRSError:
        return GeoCoordinate(error="INVALID_MGRS")

    return GeoCoordinate(lat=lat, lon=lon)
