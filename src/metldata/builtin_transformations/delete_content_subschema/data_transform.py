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
#

"""Logic for transforming data."""

from contextlib import suppress

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.data_transform import (
    get_class_resources,
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.delete_content_subschema.instruction import (
    DeleteContentSubschemaInstruction,
)


def delete_subschema_properties(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[DeleteContentSubschemaInstruction]],
) -> DataPack:
    """Delete the provided content properties from the provided data.

    Args:
        data:
            The data based on DataPack to delete the content properties from.
        properties_by_class:
            A dictionary mapping class names to lists of content properties to delete.

    Returns:
        The data with the specified content properties being deleted.
    """
    modified_data = data_to_dict(data)

    for class_name, instructions in instructions_by_class.items():
        target_resources = get_class_resources(
            data=modified_data, class_name=class_name
        )
        for instruction in instructions:
            content_path = instruction.content_path

            # resolve is one layer to deep, go one step up in content path
            path_parent, _, target_property = content_path.rpartition(".")
            for resource in target_resources.values():
                if not path_parent:
                    # property directly in top level content
                    with suppress(KeyError):
                        del resource["content"][target_property]
                else:
                    # nested property
                    target = resolve_data_object_path(
                        data=resource["content"], path=path_parent
                    )
                    with suppress(KeyError):
                        del target[target_property]

    return DataPack.model_validate(modified_data)
