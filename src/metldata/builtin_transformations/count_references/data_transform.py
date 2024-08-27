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

"""Logic for transforming data."""

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)
from metldata.transform.base import EvitableTransformationError


def count_references(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[AddReferenceCountPropertyInstruction]],
) -> DataPack:
    """Given a data pack and a dictionary of instructions by class,
    counts the references and adds the value to its corresponding content property.

    Args:
        data:
            The datapack to add the reference count values.
        instructions_by_class:
            A dictionary mapping class names to lists of instructions.

    Returns:
        The data with the reference counts added.
    """
    modified_data = data.model_copy(deep=True)
    for class_name, instructions in instructions_by_class.items():
        resources = modified_data.resources.get(class_name)

        if not resources:
            raise EvitableTransformationError()

        for instruction in instructions:
            for path_element in instruction.source_relation_path.elements:
                relation_slot = path_element.property

                for resource in resources.values():
                    related_to = resource.relations.get(relation_slot)
                    if not related_to:
                        raise EvitableTransformationError()

                    count = len(related_to) if related_to else 0

                    resource.content[instruction.target_content.object_path].update(
                        {instruction.target_content.property_name: count}
                    )

    return modified_data
