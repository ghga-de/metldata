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


class TransformationContext:
    """Context for a data transformation process, wrapping the Datapack to be
    transformed and transformation instructions per class.
    """

    def __init__(
        self,
        data: DataPack,
        instructions_by_class: dict[str, list[CountContentValueInstruction]],
    ):
        self.data = data.model_copy(deep=True)
        self.instructions_by_class = instructions_by_class

    def get_class_resources(self, class_name: str):
        """Extract the resources of a given class from a Datapack."""
        resources = self.data.resources.get(class_name)
        if not resources:
            raise EvitableTransformationError()
        return resources


def count_content(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[CountContentValueInstruction]],
) -> DataPack:
    """Transforms the data."""
    context = TransformationContext(data, instructions_by_class)
    for class_name, instructions in context.instructions_by_class.items():
        target_resources = context.get_class_resources(class_name)

        for instruction in instructions:
            relation_path = instruction.source.relation_path
            referenced_class = get_directly_referenced_class(relation_path)

            # Only one element is expected in the path
            relation_name = relation_path.elements[0].property
            # content_resources keeping the values to be counted are obtained from
            # the class that is referenced by the transformation target class through
            # relation_name.
            content_resources = context.get_class_resources(referenced_class)

            transform_resources(
                target_resources=target_resources,
                relation_name=relation_name,
                content_resources=content_resources,
                instruction=instruction,
            )

    return context.data


def transform_resources(
    *,
    target_resources: dict[ResourceId, Resource],
    relation_name: str,
    content_resources: dict[ResourceId, Resource],
    instruction: CountContentValueInstruction,
):
    """Transform resources"""
    for target_resource in target_resources.values():
        target_content = target_resource.content
        related_to = target_resource.relations.get(relation_name)
        if not related_to:
            raise EvitableTransformationError()
        count_values = get_count_values(related_to, content_resources, instruction)

        target_object = get_target_object(target_content, instruction)
        target_property = instruction.target_content.property_name
        target_object[target_property] = dict(Counter(count_values))


def get_count_values(
    resource_relations: ResourceId | ResourceIdSet,
    content_resources: dict[ResourceId, Resource],
    instruction: CountContentValueInstruction,
):
    """Get values to be counted."""
    try:
        content_values = [
            content_resources[relation].content.get(instruction.source.content_path)
            for relation in resource_relations
        ]
        return content_values
    except KeyError as exc:
        raise EvitableTransformationError() from exc


def get_target_object(
    content: dict[str, Any], instruction: CountContentValueInstruction
):
    """Get the json object that is to be modify."""
    target_object = resolve_data_object_path(
        data=content,
        path=instruction.target_content.object_path,
    )
    if (
        not isinstance(target_object, dict)
        or instruction.target_content.property_name in target_object
    ):
        raise EvitableTransformationError()

    return target_object
