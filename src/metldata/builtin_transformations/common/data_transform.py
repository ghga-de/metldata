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

"""Data transformation for resolving a relation path, calculating new values based on a
specific slot and adding those to a datapack.
"""

from collections.abc import Callable
from typing import Any

from schemapack._internals.spec.custom_types import ResourceId
from schemapack._internals.spec.datapack import ResourceIdSet
from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.custom_types import (
    MutableClassResources,
    MutableDatapack,
    MutableResource,
    MutableResourceContent,
    ResolveRelations,
)
from metldata.builtin_transformations.common.instruction import (
    TargetInstructionProtocol,
    TargetSourceInstruction,
    TargetSourceInstructionProtocol,
)
from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.resolve_path import (
    resolve_data_object_path,
    resolve_path,
)
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.transform.exceptions import EvitableTransformationError


def get_class_resources(
    *, data: MutableDatapack, class_name: str
) -> MutableClassResources:
    """Extract the resources of a given class from the dictionary."""
    resources = data["resources"].get(class_name)
    if not resources:
        raise EvitableTransformationError()
    return resources


def _resolve_relations(data: DataPack) -> ResolveRelations:
    """Retains resolve_path function's access to a datapack argument."""

    def partial_resolve_relations(
        source_resource_id: ResourceId, path: RelationPath
    ) -> frozenset[ResourceId]:
        return resolve_path(data=data, source_resource_id=source_resource_id, path=path)

    return partial_resolve_relations


def transform_data(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[TargetSourceInstruction]],
    calculate_value: Callable,
) -> DataPack:
    """Apply all transformation instructions."""
    modified_data = data_to_dict(data)

    for class_name, instructions in instructions_by_class.items():
        transform_class(
            class_name=class_name,
            data=modified_data,
            instructions=instructions,
            resolve_relations=_resolve_relations(data=data),
            calculate_value=calculate_value,
        )

    return DataPack.model_validate(modified_data)


def transform_class(
    *,
    class_name: str,
    data: MutableDatapack,
    instructions: list[TargetSourceInstruction],
    resolve_relations: ResolveRelations,
    calculate_value: Callable,
) -> None:
    """Apply the count content value transformations to the specified class."""
    # the target prefix refers to resources that will be modified by the transformation
    target_resources = get_class_resources(data=data, class_name=class_name)

    for instruction in instructions:
        path = instruction.source.relation_path
        referenced_class = path.target

        # get resources for the class referenced by the relation path
        referenced_resources = get_class_resources(
            data=data, class_name=referenced_class
        )
        for resource_id, resource in target_resources.items():
            relation_target_ids = resolve_relations(
                resource_id,
                path,
            )
            transform_resource(
                referenced_resources=referenced_resources,
                target_resource=resource,
                relation_target_ids=relation_target_ids,
                instruction=instruction,
                calculate_value=calculate_value,
            )


def transform_resource(
    *,
    referenced_resources: MutableClassResources,
    target_resource: MutableResource,
    relation_target_ids: frozenset[str],
    instruction: TargetSourceInstructionProtocol,
    calculate_value: Callable,
) -> None:
    """Apply the count content value transformation to each resource of a class."""
    target_content = target_resource.get("content")
    if target_content is None:
        raise EvitableTransformationError()

    source_values = get_source_values(
        relation_target_ids=relation_target_ids,
        referenced_resources=referenced_resources,
        content_path=instruction.source.content_path,
    )
    target_object = get_modification_target(
        data=target_content, instruction=instruction
    )
    target_property = instruction.target_content.property_name
    target_object[target_property] = calculate_value(source_values)


def get_source_values(
    *,
    relation_target_ids: ResourceId | ResourceIdSet,
    referenced_resources: MutableClassResources,
    content_path: str,
) -> list[Any]:
    """Get countable properties from all resources referred to by the relation."""
    try:
        return [
            resolve_data_object_path(
                referenced_resources[resource_id]["content"], content_path
            )
            for resource_id in relation_target_ids
        ]
    except KeyError as exc:
        raise EvitableTransformationError() from exc


def get_modification_target(
    *, data: MutableResourceContent, instruction: TargetInstructionProtocol
) -> Any:
    """Get the json object that is to be modified."""
    path = instruction.target_content.object_path
    property = instruction.target_content.property_name

    target = resolve_data_object_path(data=data, path=path)
    if not isinstance(target, dict) or property in target:
        raise EvitableTransformationError()
    return target
