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
"""Data transformation logic for the add content properties transformation."""

from copy import deepcopy

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.add_content_properties.instruction import (
    AddContentPropertyInstruction,
)
from metldata.builtin_transformations.common.data_transform import (
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.transform.exceptions import EvitableTransformationError


def add_properties(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[AddContentPropertyInstruction]],
) -> DataPack:
    """Given a data pack and a dictionary of instructions by class, add the specified
    content properties to the data.

    Args:
        data:
            The datapack to add the content properties to.
        instructions_by_class:
            A dictionary mapping class names to lists of instructions.

    Returns:
        The data with the specified content properties being added.
    """
    modified_data = data_to_dict(data)
    for class_name, instructions in instructions_by_class.items():
        class_resources = modified_data["resources"].get(class_name)

        if not class_resources:
            raise EvitableTransformationError()

        for resource in class_resources.values():
            for instruction in instructions:
                object = resolve_data_object_path(
                    data=resource["content"],
                    path=instruction.target_content.object_path,
                )

                if (
                    not isinstance(object, dict)
                    or instruction.target_content.property_name in object
                ):
                    raise EvitableTransformationError()

                object[instruction.target_content.property_name] = deepcopy(
                    instruction.value
                )
    return DataPack.model_validate(modified_data)
