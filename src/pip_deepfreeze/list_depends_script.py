#!/usr/bin/env python
"""List installed dependencies of a distribution.

This currently assumes pkg_resources is installed.

This script must be python 2 compatible.
"""

import argparse

import pkg_resources


def main(distname):
    # type: (str) -> None
    res = set()
    seen = set()

    def add(req, deps_only):
        # type: (pkg_resources.Requirement, bool) -> None
        seen_key = (req.key, req.extras)
        if seen_key in seen:
            return
        seen.add(seen_key)
        try:
            dist = pkg_resources.get_distribution(req.key)
        except pkg_resources.DistributionNotFound:
            return
        else:
            if not deps_only:
                res.add(req.key)
            for dep in dist.requires(req.extras):
                add(dep, deps_only=False)

    req = pkg_resources.Requirement.parse(distname)
    add(req, deps_only=True)

    for r in sorted(res):
        print(r)


parser = argparse.ArgumentParser(
    description="List dependencies of an installed distribution."
)
parser.add_argument("distname", metavar="DISTRIBUTION")
args = parser.parse_args()
main(args.distname)
