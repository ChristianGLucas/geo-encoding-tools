from gen.messages_pb2 import GeohashCell, GeohashEncodeInput
from nodes.geohash_decode import geohash_decode
from nodes.geohash_encode import geohash_encode
from nodes.geohash_neighbors import geohash_neighbors
from nodes.testkit import ax


def test_neighbor_matches_a_bbox_shift_computed_independently_of_get_adjacent():
    # Independent oracle: GeohashNeighbors is built on pygeohash's
    # get_adjacent, which walks precomputed base32 adjacency tables. This
    # cross-checks its N/S/E/W answers against a geometrically-derived
    # route that never calls get_adjacent: decode the cell to its bounding
    # box (a different pygeohash code path), shift the center by exactly one
    # cell-width/height in that compass direction, and re-encode. Two
    # independently-implemented paths (adjacency table vs. decode+shift+
    # encode) agreeing is real evidence of correctness, not self-consistency.
    gh = "u4pruyd"
    decoded = geohash_decode(ax(), GeohashCell(geohash=gh))
    cell_h = decoded.max_lat - decoded.min_lat
    cell_w = decoded.max_lon - decoded.min_lon

    def shifted(dlat, dlon):
        return geohash_encode(
            ax(), GeohashEncodeInput(lat=decoded.lat + dlat, lon=decoded.lon + dlon, precision=len(gh))
        ).geohash

    result = geohash_neighbors(ax(), GeohashCell(geohash=gh))
    assert result.error == ""
    assert result.n == shifted(cell_h, 0)
    assert result.s == shifted(-cell_h, 0)
    assert result.e == shifted(0, cell_w)
    assert result.w == shifted(0, -cell_w)
    assert result.ne == shifted(cell_h, cell_w)
    assert result.sw == shifted(-cell_h, -cell_w)


def test_neighbors_known_values_regression():
    # Golden/regression values (not the oracle above, but a fixed known-good
    # snapshot worth pinning so a dependency bump can't silently change them).
    result = geohash_neighbors(ax(), GeohashCell(geohash="u4pruyd"))
    assert result.error == ""
    assert result.n == "u4pruyf"
    assert result.s == "u4pruy6"
    assert result.e == "u4pruye"
    assert result.w == "u4pruy9"
    assert result.ne == "u4pruyg"
    assert result.nw == "u4pruyc"
    assert result.se == "u4pruy7"
    assert result.sw == "u4pruy3"


def test_neighbors_are_all_distinct_and_same_precision():
    result = geohash_neighbors(ax(), GeohashCell(geohash="dr5ru6j28"))
    assert result.error == ""
    cells = [result.n, result.ne, result.e, result.se, result.s, result.sw, result.w, result.nw]
    assert len(set(cells)) == 8
    assert all(len(c) == len("dr5ru6j28") for c in cells)


def test_neighbors_diagonal_agrees_regardless_of_step_order():
    # A diagonal neighbor (e.g. NE) must reach the same cell whether composed
    # N-then-E or E-then-N -- checked against the node's own two-step
    # composition path with the argument order swapped.
    import pygeohash as pgh

    gh = "9q8yyk8"
    result = geohash_neighbors(ax(), GeohashCell(geohash=gh))
    n_then_e = pgh.get_adjacent(pgh.get_adjacent(gh, "top"), "right")
    e_then_n = pgh.get_adjacent(pgh.get_adjacent(gh, "right"), "top")
    assert n_then_e == e_then_n == result.ne


def test_neighbors_empty_geohash_is_structured_error():
    result = geohash_neighbors(ax(), GeohashCell(geohash=""))
    assert result.error == "EMPTY_GEOHASH"


def test_neighbors_invalid_geohash_is_structured_error():
    result = geohash_neighbors(ax(), GeohashCell(geohash="a1i0"))
    assert result.error == "INVALID_GEOHASH"
