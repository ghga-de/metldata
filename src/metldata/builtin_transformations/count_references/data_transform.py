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

from metldata.builtin_transformations.common.resolve_path import resolve_path
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


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
    modified_data = data_to_dict(data)
    for class_name, instructions in instructions_by_class.items():
        resources = modified_data["resources"].get(class_name)
        if not resources:
            raise EvitableTransformationError()

        for instruction in instructions:
            path = instruction.source_relation_path

            for resource_id, resource in resources.items():
                target_resource_ids = resolve_path(
                    data=data,
                    source_resource_id=resource_id,
                    path=path,
                )
                count = len(target_resource_ids or [])
                resource["content"][instruction.target_content.object_path].update(
                    {instruction.target_content.property_name: count}
                )

    return DataPack.model_validate(modified_data)
