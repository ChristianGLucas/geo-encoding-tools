# geo-encoding-tools

Composable **geospatial encoding** nodes for the [Axiom](https://axiomide.com)
marketplace, published as `christiangeorgelucas/geo-encoding-tools`. Encode
and decode geohashes, and convert coordinates across **lat/lon, UTM (Universal
Transverse Mercator), and MGRS (the military grid reference system)** —
entirely offline and deterministically.

This is a flow-neighbor of
[`christiangeorgelucas/geo-tools`](https://github.com/ChristianGLucas/geo-tools)
(2D geometry: distance/area/centroid/...), not a replacement for it: geo-tools
measures and transforms geometry, this package encodes/decodes point
*representations*. Field names (`lat`, `lon`, decimal degrees, WGS-84) match
geo-tools' convention so a point flows between the two packages without
renaming, and `GeohashDecode`'s bounding box is additionally emitted as a
GeoJSON polygon so it chains straight into geo-tools' geometry-consuming nodes
(`Area`, `Centroid`, `Contains`, ...).

Written in **Python**, wrapping three battle-tested, permissively-licensed
libraries:

| Concern | Library | License |
|---|---|---|
| Geohash encode/decode/neighbors | [`pygeohash`](https://github.com/wdm0006/pygeohash) | Apache-2.0 / MIT / BSD (triple-licensed) |
| Lat/lon &harr; UTM | [`utm`](https://github.com/Turbo87/utm) (Turbo87) | MIT |
| Lat/lon &harr; MGRS, UTM &harr; MGRS | [`mgrs`](https://github.com/hobuinc/mgrs) (hobuinc) | MIT wrapper over NGA's public-domain GEOTRANS C core |

See `THIRD_PARTY_NOTICES.md` for how each license (including the GEOTRANS
core's US-government public-domain status) was independently verified from
source.

Every node is **stateless**, **offline** (no network, no API keys, no
signup), and **deterministic**.

## Nodes

| Node | Input &rarr; Output | Purpose |
|---|---|---|
| `GeohashEncode` | `GeohashEncodeInput` &rarr; `EncodedGeohash` | Lat/lon &rarr; geohash string at a given precision (1-12 chars) |
| `GeohashDecode` | `GeohashCell` &rarr; `DecodedGeohash` | Geohash &rarr; center point, +/- error margins, bounding box (+ GeoJSON) |
| `GeohashNeighbors` | `GeohashCell` &rarr; `GeohashNeighborhood` | The 8 compass-adjacent cells (N/NE/E/SE/S/SW/W/NW) |
| `GeohashCompare` | `GeohashPair` &rarr; `GeohashRelation` | Spatial containment (prefix relationship) + longest common prefix |
| `LatLonToUTM` | `GeoCoordinate` &rarr; `UTMCoordinate` | Lat/lon &rarr; UTM zone/hemisphere/easting/northing |
| `UTMToLatLon` | `UTMCoordinate` &rarr; `GeoCoordinate` | UTM &rarr; lat/lon |
| `LatLonToMGRS` | `MGRSEncodeInput` &rarr; `MGRSCoordinate` | Lat/lon &rarr; MGRS string at a given precision (0-5 digit pairs) |
| `MGRSToLatLon` | `MGRSCoordinate` &rarr; `GeoCoordinate` | MGRS &rarr; lat/lon |
| `UTMToMGRS` | `UTMCoordinate` &rarr; `MGRSCoordinate` | UTM &rarr; MGRS, no lat/lon round-trip |
| `MGRSToUTM` | `MGRSCoordinate` &rarr; `UTMCoordinate` | MGRS &rarr; UTM, no lat/lon round-trip |

Every point input is validated: `lat` outside [-90, 90] or `lon` outside
[-180, 180] returns `INVALID_LAT`/`INVALID_LON` rather than a silently wrong
answer. UTM is only defined for latitudes -80 to 84 (the polar caps are
excluded, covered by UPS instead); a latitude outside that band returns
`OUT_OF_RANGE`. **MGRS has no such restriction** — it covers the poles too
via UPS internally — so `LatLonToMGRS` succeeds where `LatLonToUTM` would not.

`UTMCoordinate` deliberately uses a plain `hemisphere` (`"N"`/`"S"`) rather
than the MGRS latitude-band letter (e.g. `'U'`, `'T'`) some libraries bundle
into "UTM zone" — that band letter is an MGRS grid concept, not part of true
UTM, and conflating the two is a common correctness bug this envelope avoids
by construction.

### Caveats (honest edges)

- **`GeohashNeighbors` near a pole**: a neighbor search can recurse off the
  edge of the base32 grid at extreme latitudes and returns
  `NEIGHBOR_UNDEFINED_AT_EDGE` rather than a nonsensical cell.
- **`GeohashCompare`'s containment is a prefix check, not a general spatial
  test**: `a_contains_b` is true iff `geohash_a`'s characters are an exact
  prefix of `geohash_b`'s — which for geohashes is exactly spatial
  containment, but it means the two hashes must actually share a common
  grid ancestry (encoded at the same alignment), not merely overlap
  geographically.
- **`UTMToMGRS` always encodes at full (5-digit, 1m) MGRS precision** — a UTM
  coordinate's easting/northing are already full-precision doubles with no
  separate "how many digits" concept of their own to forward.

## Development

```bash
axiom validate     # static checks
axiom test         # unit tests (goldens + independent oracles + error paths)
axiom dev          # local HTTP bridge (prints the port it binds)
```

## Correctness

The test suite enforces every accuracy claim with **independent oracles**,
never just a round-trip through the same library:

- **Geohash encode/decode** is checked against the worked example published
  in Wikipedia's [Geohash](https://en.wikipedia.org/wiki/Geohash) article
  (`(42.6, -5.6)` at precision 5 &rarr; `"ezs42"`, decoding to the documented
  interval).
- **`GeohashNeighbors`** is cross-checked against a geometrically independent
  path: decode the cell to its bounding box, shift the center by exactly one
  cell-width/height in the target direction, and re-encode — a different
  pygeohash code path (decode+encode) than the adjacency-table lookup
  `get_adjacent` itself uses, so agreement is real evidence, not
  self-consistency.
- **UTM** is checked against the CN Tower's published position (Wikipedia's
  [MGRS](https://en.wikipedia.org/wiki/Military_Grid_Reference_System)
  article: `43°38'33.24"N 79°23'13.7"W` &rarr; `17N 630084 4833438`).
- **UTM &harr; MGRS** is checked against the worked pair published in
  Wikipedia's
  [UTM](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system)
  article (`31N 303760 5787415` &harr; `31U CT 03760 87415`), independent of
  any lat/lon round trip.

## Composability

`GeohashDecode`'s `geojson` field is a GeoJSON Polygon string using the same
convention as `christiangeorgelucas/geo-tools`' `Geometry`/`BoundingBox`
messages, so a geohash cell's footprint can be measured, tested for
containment, or combined with other geometry directly by that package's
nodes.

## License

MIT — (c) 2026 Christian George Lucas. Built for the Axiom marketplace.
See `THIRD_PARTY_NOTICES.md` for the wrapped libraries' licenses.
