import pygeohash as pgh

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import DecodedGeohash, GeohashCell
from nodes._common import GeoEncodingError, bbox_to_geojson_polygon, validate_geohash_string


def geohash_decode(ax: AxiomContext, input: GeohashCell) -> DecodedGeohash:
    """Decode a geohash back to its center point, +/- error margins (the
    half-width of the cell on each axis -- the true encoded point could be
    anywhere within center +/- error), and bounding box, via pygeohash's
    decode_exactly. `geojson` carries the same box as a GeoJSON Polygon
    string so it chains directly into christiangeorgelucas/geo-tools'
    Geometry-consuming nodes (Area, Centroid, Contains, ...).
    """
    try:
        geohash = validate_geohash_string(input.geohash)
        lat, lon, lat_err, lon_err = pgh.decode_exactly(geohash)
    except GeoEncodingError as e:
        return DecodedGeohash(error=e.token)
    except ValueError:
        return DecodedGeohash(error="INVALID_GEOHASH")

    min_lat, max_lat = lat - lat_err, lat + lat_err
    min_lon, max_lon = lon - lon_err, lon + lon_err
    return DecodedGeohash(
        lat=lat,
        lon=lon,
        lat_error=lat_err,
        lon_error=lon_err,
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
        geojson=bbox_to_geojson_polygon(min_lon, min_lat, max_lon, max_lat),
    )
