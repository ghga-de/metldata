# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.common.custom_types import ResourceId
from metldata.builtin_transformations.common.utils import data_to_dict
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
    modified_data = data_to_dict(data)

    target_class_resources = data.resources.get(target_class)
    if target_class_resources is None:
        raise EvitableTransformationError()

    modified_resources = modified_data["resources"][target_class]

    for resource_id, resource in target_class_resources.items():
        targets = get_all_targets(resource, source_relations)

        modified_resources[resource_id]["relations"][target_relation] = {
            "targetClass": targets.target_class,
            "targetResources": set().union(*targets.target_resources),
        }

        # Remove source relations
        for relation_name in source_relations:
            del modified_resources[resource_id]["relations"][relation_name]

    return DataPack.model_validate(modified_data)


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
