#!/usr/bin/env python
"""List dependencies of a distribution.

This currently assumes pkg_resources is installed.

This script must be python 2 compatible.
"""

import pkg_resources


def main(distname):
    res = set()
    seen = set()

    def add(deps):
        for dep in deps:
            seen_key = (dep.key, dep.extras)
            if seen_key in seen:
                continue
            seen.add(seen_key)
            res.add(dep.key)
            add(d for d in pkg_resources.get_distribution(dep).requires(dep.extras))

    req = pkg_resources.Requirement.parse(distname)
    add(d for d in pkg_resources.get_distribution(req.name).requires(req.extras))

    for r in sorted(res):
        print(r)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="List dependencies of an installed distribution."
    )
    parser.add_argument("distname", metavar="DISTRIBUTION")
    args = parser.parse_args()
    main(args.distname)