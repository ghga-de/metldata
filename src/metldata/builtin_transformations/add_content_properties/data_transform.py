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
from metldata.builtin_transformations.add_content_properties.path import (
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.utils import thaw_frozen_dict
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
    updated_classes: dict = {}

    for class_name, instructions in instructions_by_class.items():
        class_resources = data.resources.get(class_name)

        if not class_resources:
            raise EvitableTransformationError()

        # convert to a mutable dict to modify it
        # note that, it does not apply mutability to inner layer Resource objects
        mutable_class_resources = thaw_frozen_dict(class_resources)

        for resource_id, resource in class_resources.items():
            resource_content = thaw_frozen_dict(resource.content)
            for instruction in instructions:
                object = resolve_data_object_path(
                    data=resource_content,
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
            # resource_content changed
            mutable_class_resources[resource_id] = resource.model_copy(
                update={"content": resource_content})
        #class resources changed
        updated_classes[class_name]= class_resources.update(mutable_class_resources)
    # resources changed
    updated_resources = data.resources.update(updated_classes)
    modified_data = data.model_copy(update={"resources": updated_resources})
    return modified_data
