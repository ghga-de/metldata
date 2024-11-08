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

"""Data transformation logic for count content values transformation."""

from collections import Counter
from typing import Any

from schemapack._internals.spec.custom_types import ResourceId
from schemapack._internals.spec.datapack import ResourceIdSet
from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.path.path_utils import (
    get_directly_referenced_class,
)
from metldata.builtin_transformations.count_content_values.instruction import (
    CountContentValueInstruction,
)
from metldata.transform.exceptions import (
    EvitableTransformationError,
)


def get_class_resources(*, data: DataPack, class_name: str):
    """Extract the resources of a given class from a Datapack."""
    resources = data.resources.get(class_name)
    if not resources:
        raise EvitableTransformationError()
    return resources


def count_content(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[CountContentValueInstruction]],
) -> DataPack:
    """Apply all count content value transformation instructions."""
    data = data.model_copy(deep=True)

    for class_name, instructions in instructions_by_class.items():
        transform_class(class_name=class_name, data=data, instructions=instructions)
    return data


def transform_class(
    *, class_name: str, data: DataPack, instructions: list[CountContentValueInstruction]
):
    """Apply the count content value transformations to the specified class."""
    # the target prefix refers to resources that will be modified by the transformation
    target_resources = get_class_resources(data=data, class_name=class_name)
    for instruction in instructions:
        relation_path = instruction.source.relation_path
        referenced_class = get_directly_referenced_class(relation_path)

        # Only one element is expected in the path, validated by `get_directly_referenced_class`
        relation_name = relation_path.elements[0].property
        # get resources for the class referenced by the relation path
        referenced_resources = get_class_resources(
            data=data, class_name=referenced_class
        )

        for target_resource in target_resources.values():
            transform_resource(
                referenced_resources=referenced_resources,
                target_resource=target_resource,
                relation_name=relation_name,
                instruction=instruction,
            )


def transform_resource(
    *,
    referenced_resources: dict[ResourceId, Resource],
    target_resource: Resource,
    relation_name: str,
    instruction: CountContentValueInstruction,
):
    """Apply the count content value transformation to each resource of a class."""
    target_content = target_resource.content
    relation_target_ids = target_resource.relations.get(relation_name)
    if not relation_target_ids:
        raise EvitableTransformationError()

    values_to_count = get_values_to_count(
        relation_target_ids=relation_target_ids,
        referenced_resources=referenced_resources,
        content_path=instruction.source.content_path,
    )
    target_object = get_modification_target(
        data=target_content, instruction=instruction
    )
    target_property = instruction.target_content.property_name
    target_object[target_property] = dict(Counter(values_to_count))


def get_values_to_count(
    *,
    relation_target_ids: ResourceId | ResourceIdSet,
    referenced_resources: dict[ResourceId, Resource],
    content_path: str,
):
    """Get countable properties from all resources referred to by the relation."""
    try:
        return [
            referenced_resources[resource_id].content.get(content_path)
            for resource_id in relation_target_ids
        ]
    except KeyError as exc:
        raise EvitableTransformationError() from exc


def get_modification_target(
    *, data: dict[str, Any], instruction: CountContentValueInstruction
):
    """Get the json object that is to be modified."""
    path = instruction.target_content.object_path
    property = instruction.target_content.property_name

    target = resolve_data_object_path(data=data, path=path)
    if not isinstance(target, dict) or property in target:
        raise EvitableTransformationError()
    return target
