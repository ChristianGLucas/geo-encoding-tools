import pygeohash as pgh

from gen.axiom_context import AxiomContext
from gen.messages_pb2 import GeohashCell, GeohashNeighborhood
from nodes._common import GEOHASH_ALPHABET, GeoEncodingError, validate_geohash_string

# The 8 compass neighbors, each composed from pygeohash's 4 primitive
# directions (top/bottom/left/right). pygeohash's get_adjacent already
# handles the base32 alphabet's non-trivial parent-cell border wraparound
# (see geohash-js, which it ports) -- composing two calls for a diagonal is
# plain function composition, not a reimplementation of that logic.
_STEPS = {
    "n": ("top",), "s": ("bottom",), "e": ("right",), "w": ("left",),
    "ne": ("top", "right"), "nw": ("top", "left"),
    "se": ("bottom", "right"), "sw": ("bottom", "left"),
}


def geohash_neighbors(ax: AxiomContext, input: GeohashCell) -> GeohashNeighborhood:
    """The 8 geohashes adjacent to a cell (N/NE/E/SE/S/SW/W/NW), at the same
    precision as the input, via pygeohash's get_adjacent.
    """
    try:
        geohash = validate_geohash_string(input.geohash)
        if any(c not in GEOHASH_ALPHABET for c in geohash):
            # get_adjacent has no full-string charset check of its own (it
            # only looks at one character at a time via table lookups, which
            # can raise a generic, indistinguishable ValueError on a bad
            # char) -- so this package validates the charset itself, the
            # same way GeohashCompare does, to tell that case apart from the
            # genuine pole/edge case caught below.
            raise GeoEncodingError("INVALID_GEOHASH", f"{geohash!r} contains a non-base32 character")

        cells = {}
        for name, steps in _STEPS.items():
            gh = geohash
            for step in steps:
                gh = pgh.get_adjacent(gh, step)
            cells[name] = gh
        return GeohashNeighborhood(**cells)
    except GeoEncodingError as e:
        return GeohashNeighborhood(error=e.token)
    except ValueError:
        # pygeohash's own "geohash length cannot be 0" case: a neighbor
        # search recursed off the edge of the grid near a pole -- a real, if
        # rare, boundary condition, not malformed input (already ruled out
        # above).
        return GeohashNeighborhood(error="NEIGHBOR_UNDEFINED_AT_EDGE")
