#!/usr/bin/env python
"""List installed distributions with some of their metadata in json format.

This currently assumes pkg_resources is installed.
In environments without setuptools, we'll use 'pip inspect'.

This script must be python 2 compatible.
"""

import json
import sys

try:
    from typing import Any, Dict
except ImportError:
    pass

import pkg_resources


def _req_name_with_extras(req):
    # type: (pkg_resources.Requirement) -> str
    if req.extras:
        return "{}[{}]".format(req.project_name, ",".join(sorted(req.extras)))
    else:
        return req.project_name


def main():
    # type: () -> None
    recs = []
    ws = pkg_resources.working_set
    for dist in ws:
        rec = {}  # type: Dict[str, Any]
        metadata = {}  # type: Dict[str, Any]
        metadata["name"] = dist.project_name
        metadata["version"] = dist.version
        requires_dist = [str(dep) for dep in dist.requires(tuple(dist.extras))]
        # sort for easier testing
        if requires_dist:
            metadata["requires_dist"] = sorted(requires_dist)
        if dist.extras:
            metadata["provides_extra"] = sorted(dist.extras)
        rec["metadata"] = metadata
        if dist.has_metadata("direct_url.json"):
            direct_url = json.loads(dist.get_metadata("direct_url.json"))
            rec["direct_url"] = direct_url
        # requires/extra_requires
        # XXX: this part would not be necessary if `packaging` had a way
        #      to check the extra marker without evaluating with the full
        #      environment
        requires = []
        requires_set = set()
        for dep in dist.requires():
            requires.append(_req_name_with_extras(dep))
            requires_set.add(dep.key)
        if requires:
            rec["requires"] = requires
        if dist.extras:
            extra_requires = {}
            for extra in dist.extras:
                extra_requires[extra] = [
                    _req_name_with_extras(dep)
                    for dep in dist.requires((extra,))
                    if dep.key not in requires_set
                ]
            rec["extra_requires"] = extra_requires
        recs.append(rec)
    json.dump(recs, sys.stdout, indent=2)
    sys.stdout.write("\n")


main()
