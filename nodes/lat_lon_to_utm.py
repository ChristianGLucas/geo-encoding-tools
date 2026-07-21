import utm

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import GeoCoordinate, UTMCoordinate
from nodes._common import (
    GeoEncodingError,
    band_letter_to_hemisphere,
    validate_point,
    validate_utm_lat_band,
)


def lat_lon_to_utm(ax: AxiomContext, input: GeoCoordinate) -> UTMCoordinate:
    """Convert a lat/lon point to a Universal Transverse Mercator (UTM)
    coordinate, via Turbo87/utm. UTM is only defined for latitudes -80 to 84
    (the polar caps are covered by UPS instead); a latitude outside that band
    returns OUT_OF_RANGE.
    """
    try:
        validate_point(input.lat, input.lon)
        validate_utm_lat_band(input.lat)
        easting, northing, zone_number, zone_letter = utm.from_latlon(input.lat, input.lon)
    except GeoEncodingError as e:
        return UTMCoordinate(error=e.token)
    except utm.error.OutOfRangeError:
        return UTMCoordinate(error="OUT_OF_RANGE")

    return UTMCoordinate(
        zone_number=zone_number,
        hemisphere=band_letter_to_hemisphere(zone_letter),
        easting=easting,
        northing=northing,
    )
