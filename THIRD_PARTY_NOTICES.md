# Third-party notices

christiangeorgelucas/geo-encoding-tools wraps three permissively-licensed
libraries. Each was independently verified from source (not from package
metadata alone) before inclusion.

## pygeohash

- PyPI: [`pygeohash`](https://pypi.org/project/pygeohash/) 3.3.1
- Source: [wdm0006/pygeohash](https://github.com/wdm0006/pygeohash)
- License: triple-licensed, pick one — Apache License 2.0, MIT License, or
  New BSD License (see the repo's `LICENSE` file). Used here under the MIT
  option.

## utm

- PyPI: [`utm`](https://pypi.org/project/utm/) 0.8.1
- Source: [Turbo87/utm](https://github.com/Turbo87/utm)
- License: MIT.

## mgrs

- PyPI: [`mgrs`](https://pypi.org/project/mgrs/) 1.5.4
- Source: [hobuinc/mgrs](https://github.com/hobuinc/mgrs)
- License: the Python wrapper is MIT (`Copyright (c) 2016 Howard Butler`,
  repo `LICENSE` file). The bundled C core (`libmgrs/*.c` — `mgrs.c`,
  `utm.c`, `tranmerc.c`, `polarst.c`, `ups.c`) is NGA's GEOTRANS, developed
  by the U.S. Army Topographic Engineering Center. Its own file header
  states "LICENSES: None apply to this component" — the standard GEOTRANS
  disclaimer for a work of the U.S. federal government, which is not
  eligible for copyright in the United States (17 U.S.C. Section 105) and is
  therefore public domain. The repository's MIT `LICENSE` covers the
  packaged distribution as a whole.

All three libraries are used as compiled/interpreted dependencies via
`requirements.txt`, unmodified, with no vendored or embedded source.
