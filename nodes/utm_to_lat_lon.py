import utm

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import GeoCoordinate, UTMCoordinate
from nodes._common import GeoEncodingError, validate_utm


def utm_to_lat_lon(ax: AxiomContext, input: UTMCoordinate) -> GeoCoordinate:
    """Convert a UTM coordinate back to lat/lon, via Turbo87/utm. Easting and
    northing range checks (a UTM coordinate must land within the projected
    zone's valid envelope) are left to the library itself, which already
    enforces them.
    """
    try:
        validate_utm(input.zone_number, input.hemisphere)
        lat, lon = utm.to_latlon(
            input.easting,
            input.northing,
            input.zone_number,
            northern=(input.hemisphere == "N"),
        )
    except GeoEncodingError as e:
        return GeoCoordinate(error=e.token)
    except utm.error.OutOfRangeError:
        return GeoCoordinate(error="OUT_OF_RANGE")

    return GeoCoordinate(lat=lat, lon=lon)
