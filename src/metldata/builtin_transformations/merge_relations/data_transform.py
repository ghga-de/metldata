# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"Logic for transforming data."

from typing import NamedTuple

from arcticfreeze import FrozenDict
from schemapack._internals.spec.datapack import ResourceRelation
from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.common.custom_types import ResourceId
from metldata.builtin_transformations.common.mutate import (
    set_class_resources,
)
from metldata.transform.exceptions import EvitableTransformationError


class Target(NamedTuple):
    """Model defining target elements."""

    target_resources: list[set[ResourceId] | ResourceId]
    target_class: str


def merge_data_relations(
    *,
    data: DataPack,
    target_class: str,
    target_relation: str,
    source_relations: list[str],
) -> DataPack:
    """Merge relations in the data according to the transformation configuration.
    Args:
        data: The data to be transformed.
        target_class: The name of the class to merge relations for.
        target_relation: The name of the relation to merge into.
        source_relations: List of relation names to be merged.
    """
    target_class_resources = data.resources.get(target_class)
    if target_class_resources is None:
        raise EvitableTransformationError()

    updated_resources: dict[ResourceId, Resource] = {}
    for resource_id, resource in target_class_resources.items():
        targets = get_all_targets(resource, source_relations)

        merged_relation = ResourceRelation(
            targetClass=targets.target_class,
            targetResources=frozenset().union(*targets.target_resources),
        )
        # add merged relations to resource relations
        updated_relations = {**resource.relations, target_relation: merged_relation}

        # remove individual relations that are merged from the resource
        remaining_relations = {
            name: relation
            for name, relation in updated_relations.items()
            if name not in source_relations
        }

        updated_resources[resource_id] = resource.model_copy(
            update={"relations": FrozenDict(remaining_relations)}
        )

    return set_class_resources(
        data=data, class_name=target_class, resources=updated_resources
    )


def get_all_targets(resource: Resource, source_relations: list[str]) -> Target:
    """Get target resources and the target class of the merged relations."""
    try:
        all_targets = []
        for relation_name in source_relations:
            target_resources = resource.relations[relation_name].targetResources
            if target_resources is not None:
                all_targets.append(target_resources)

        # must be same across the merging relations
        relation_target_class = resource.relations[source_relations[0]].targetClass

    except KeyError as exc:
        raise EvitableTransformationError() from exc

    return Target(target_resources=all_targets, target_class=relation_target_class)
