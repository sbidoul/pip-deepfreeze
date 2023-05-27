from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import typer
from packaging.requirements import Requirement
from packaging.utils import NormalizedName, canonicalize_name

from .installed_dist import InstalledDistribution
from .pip import pip_list
from .project_name import get_project_name
from .utils import make_project_name_with_extras

NodeKey = Tuple[NormalizedName, Tuple[NormalizedName, ...]]


def _req_name_with_extras(req: Requirement) -> str:
    if req.extras:
        return f"{req.name}[{','.join(sorted(req.extras))}]"
    return req.name


class Node:
    def __init__(self, req: Requirement, dist: Optional[InstalledDistribution]):
        self.req = req
        self.dist = dist
        self.children: List[Node] = []

    @staticmethod
    def key(req: Requirement) -> NodeKey:
        return (
            canonicalize_name(req.name),
            tuple(sorted(canonicalize_name(e) for e in req.extras)),
        )

    def print(self) -> None:
        seen: Set[Node] = set()

        def _print(indent: List[str], node: Node) -> None:
            # inspired by https://stackoverflow.com/a/59109706
            SPACE = "    "
            BRANCH = "│   "
            TEE = "├── "
            LAST = "└── "
            typer.echo(f"{''.join(indent)}{_req_name_with_extras(node.req)}", nl=False)
            if node in seen:
                typer.secho(" ⬆", dim=True)
                return
            typer.secho(f" ({node.sversion})", dim=True)
            seen.add(node)
            if not node.children:
                return
            pointers = [TEE] * (len(node.children) - 1) + [LAST]
            for pointer, child in zip(
                pointers, sorted(node.children, key=lambda n: str(n.req))
            ):
                if indent:
                    if indent[-1] == TEE:
                        _print(indent[:-1] + [BRANCH, pointer], child)
                    else:
                        assert indent[-1] == LAST
                        _print(indent[:-1] + [SPACE, pointer], child)
                else:
                    _print([pointer], child)

        _print([], self)

    @property
    def sversion(self) -> str:
        if not self.dist:
            version = typer.style("✘ not installed", fg=typer.colors.RED)
        else:
            version = self.dist.version
            if self.dist.direct_url:
                version += f" @ {self.dist.direct_url}"
        return version


def tree(python: str, project_root: Path, extras: List[NormalizedName]) -> None:
    project_name = get_project_name(python, project_root)
    installed_dists = pip_list(python)
    nodes: Dict[NodeKey, Node] = {}

    def add(req: Requirement) -> Node:
        key = Node.key(req)
        if key in nodes:
            return nodes[key]
        dist = installed_dists.get(canonicalize_name(req.name))
        node = Node(req, dist)
        nodes[key] = node
        if not dist:
            # not installed
            return node
        for dep_req in dist.requires:
            node.children.append(add(dep_req))
        for extra in req.extras:
            extra = canonicalize_name(extra)
            for dep_req in dist.extra_requires.get(extra, []):
                node.children.append(add(dep_req))
        return node

    add(Requirement(make_project_name_with_extras(project_name, extras))).print()
