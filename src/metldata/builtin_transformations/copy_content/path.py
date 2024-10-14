# Copyright 2021 - 2024 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Graph form of relation path with specific constraints for copy transformation."""

from collections import deque

from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)


class RelationPathNode:
    """Representation of a class inside a RelationPath, with incoming and outgoing relations."""

    def __init__(self, node_name: str):
        self.name: str = node_name
        self.points_to: dict[RelationPathNode, str] = dict()
        self.pointed_at_by: list[RelationPathNode] = []


class RelationPathGraph:
    """Graph representation of a RelationPath"""

    def __init__(self, relation_path: RelationPath) -> None:  # noqa: C901, PLR0912
        nodes: dict[str, RelationPathNode] = dict()

        # convert to graph nodes
        for element in relation_path.elements:
            lhs = element.lhs
            if lhs not in nodes:
                nodes[lhs] = RelationPathNode(lhs)

            rhs = element.rhs
            if rhs not in nodes:
                nodes[rhs] = RelationPathNode(rhs)
            relation_type = element.type_

            if relation_type == RelationPathElementType.ACTIVE:
                nodes[lhs].points_to[nodes[rhs]] = element.property
                nodes[rhs].pointed_at_by.append(nodes[lhs])
            else:
                nodes[rhs].points_to[nodes[lhs]] = element.property
                nodes[lhs].pointed_at_by.append(nodes[rhs])

        # find source and target nodes and check invariants
        first = None
        last = None
        for node in nodes.values():
            if not node.pointed_at_by:
                if first:
                    raise ValueError("There are multiple possible sources in the path.")
                first = node
            if not node.points_to:
                if last:
                    raise ValueError("There are multiple possible targets in the path.")
                last = node

            if first == last:
                raise ValueError("Source and target cannot be the same node.")

        if not first:
            raise ValueError("No source node parsed.")

        if not last:
            raise ValueError("No target node parsed.")

        # check if source is connected to target
        queue = deque([first])
        explored = set([first])
        while queue:
            current = queue.pop()
            if current == last:
                break
            for node in current.points_to:
                if node not in explored:
                    explored.add(node)
                    queue.append(node)
        else:
            raise ValueError("Source and target are not connected.")

        self.nodes = nodes
        self.first = first
        self.last = last
