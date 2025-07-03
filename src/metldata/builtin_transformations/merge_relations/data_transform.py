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

from typing import NamedTuple, cast

from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.common.custom_types import ResourceId
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.merge_relations.config import MergeRelationsConfig
from metldata.transform.exceptions import EvitableTransformationError


def merge_data_relations(
    *, data: DataPack, transformation_config: MergeRelationsConfig
) -> DataPack:
    """Merge relations in the data according to the transformation configuration."""
    modified_data = data_to_dict(data)

    target_class = transformation_config.class_name
    target_relation = transformation_config.target_relation
    source_relations = transformation_config.source_relations

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


class Target(NamedTuple):
    """Model defining target elements."""

    target_resources: list[set[ResourceId] | ResourceId]
    target_class: str


def get_all_targets(resource: Resource, source_relations: list[str]) -> Target:
    """Get target resources and the target class of the merged relations."""
    try:
        all_targets = [
            resource.relations[relation_name].targetResources
            for relation_name in source_relations
            if resource.relations[relation_name].targetResources is not None
        ]

        # must be same across the merging relations
        relation_target_class = resource.relations[source_relations[0]].targetClass

    except KeyError as exc:
        raise EvitableTransformationError() from exc

    # type casting in order to pass type checking for union()
    all_targets = cast(list[set[ResourceId] | ResourceId], all_targets)

    return Target(target_resources=all_targets, target_class=relation_target_class)
