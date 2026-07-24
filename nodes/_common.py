"""Shared helpers for christiangeorgelucas/geo-encoding-tools nodes.

Centralizes lat/lon range validation, geohash/MGRS string sanity checks, and
the structured-error contract every node follows: a node never raises out to
the caller — on malformed input it returns its output message with the data
fields empty and `error` set to one of the stable tokens documented on that
message. Payload size is the platform's job, not this package's — no node
here imposes a length cap on the geohash/MGRS string itself (charset
validation, which pygeohash's/mgrs's own decoders already perform, is what
actually rejects a malformed string).
"""
from __future__ import annotations

import math

# The geohash base32 alphabet (RFC-less but universally implemented this way,
# and the one pygeohash uses): 0-9 and lowercase b-z minus 'a', 'i', 'l', 'o'
# (chosen to avoid visual confusion with digits).
GEOHASH_ALPHABET = frozenset("0123456789bcdefghjkmnpqrstuvwxyz")

MIN_GEOHASH_PRECISION = 1
MAX_GEOHASH_PRECISION = 12
DEFAULT_GEOHASH_PRECISION = 9

MIN_MGRS_PRECISION = 0
MAX_MGRS_PRECISION = 5

MIN_UTM_ZONE = 1
MAX_UTM_ZONE = 60

# UTM (as opposed to MGRS, which extends over the poles via UPS) is only
# defined in this latitude band; Turbo87/utm itself enforces this, but
# checking it here lets every UTM-producing node fail the same way before
# paying for the projection math.
UTM_MIN_LAT = -80.0
UTM_MAX_LAT = 84.0


class GeoEncodingError(Exception):
    """Carries a stable, machine-readable error token."""

    def __init__(self, token: str, message: str = "") -> None:
        super().__init__(message or token)
        self.token = token


def validate_lat(lat: float) -> None:
    if not math.isfinite(lat) or not (-90.0 <= lat <= 90.0):
        raise GeoEncodingError("INVALID_LAT", f"latitude {lat!r} is not in [-90, 90]")


def validate_lon(lon: float) -> None:
    if not math.isfinite(lon) or not (-180.0 <= lon <= 180.0):
        raise GeoEncodingError("INVALID_LON", f"longitude {lon!r} is not in [-180, 180]")


def validate_point(lat: float, lon: float) -> None:
    validate_lat(lat)
    validate_lon(lon)


def validate_utm_lat_band(lat: float) -> None:
    if not (UTM_MIN_LAT <= lat <= UTM_MAX_LAT):
        raise GeoEncodingError(
            "OUT_OF_RANGE", f"latitude {lat!r} is outside UTM's defined band [-80, 84]"
        )


def validate_geohash_precision(precision: int) -> int:
    """Returns the effective precision (0/unset -> the package default)."""
    if precision == 0:
        return DEFAULT_GEOHASH_PRECISION
    if not (MIN_GEOHASH_PRECISION <= precision <= MAX_GEOHASH_PRECISION):
        raise GeoEncodingError(
            "INVALID_PRECISION", f"geohash precision {precision} is not in [1, 12]"
        )
    return precision


def validate_mgrs_precision(precision: int) -> None:
    if not (MIN_MGRS_PRECISION <= precision <= MAX_MGRS_PRECISION):
        raise GeoEncodingError(
            "INVALID_PRECISION", f"MGRS precision {precision} is not in [0, 5]"
        )


def validate_geohash_string(geohash: str) -> str:
    """Returns the lower-cased geohash. Only checks emptiness — charset
    validation is left to pygeohash's own decoder (it already raises
    ValueError on the first invalid character; duplicating that scan here
    would just be a slower, parallel copy of the same check)."""
    if not geohash:
        raise GeoEncodingError("EMPTY_GEOHASH", "geohash is required")
    return geohash.lower()


def validate_mgrs_string(mgrs_str: str) -> str:
    if not mgrs_str:
        raise GeoEncodingError("EMPTY_MGRS", "mgrs is required")
    return mgrs_str


def validate_utm(zone_number: int, hemisphere: str) -> None:
    if not (MIN_UTM_ZONE <= zone_number <= MAX_UTM_ZONE):
        raise GeoEncodingError(
            "INVALID_UTM_ZONE", f"UTM zone {zone_number} is not in [1, 60]"
        )
    if hemisphere not in ("N", "S"):
        raise GeoEncodingError(
            "INVALID_HEMISPHERE", f"hemisphere {hemisphere!r} must be 'N' or 'S'"
        )


def band_letter_to_hemisphere(zone_letter: str) -> str:
    """Turbo87/utm returns the MGRS latitude-band letter (C..X, an MGRS grid
    concept). True UTM only has a hemisphere, and the band letter maps onto
    it directly: N..X is the northern hemisphere, C..M is the southern
    (mirroring what utm.to_latlon itself does internally to interpret a band
    letter as northern=True/False)."""
    return "N" if zone_letter.upper() >= "N" else "S"


def bbox_to_geojson_polygon(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> str:
    """A GeoJSON Polygon (RFC 7946) string for an axis-aligned bounding box,
    wound counter-clockwise from the southwest corner. Matches the `geojson`
    convention of christiangeorgelucas/geo-tools's own BoundingBox/Geometry
    messages so it can be passed straight into that package's nodes."""
    ring = (
        f"[{min_lon},{min_lat}],[{max_lon},{min_lat}],"
        f"[{max_lon},{max_lat}],[{min_lon},{max_lat}],[{min_lon},{min_lat}]"
    )
    return f'{{"type":"Polygon","coordinates":[[{ring}]]}}'
