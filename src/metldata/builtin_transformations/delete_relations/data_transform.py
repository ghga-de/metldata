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

"""Logic for transforming data."""

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.delete_relations.instruction import (
    DeleteRelationInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


def delete_data_relations(
    *, data: DataPack, instructions_by_class: dict[str, list[DeleteRelationInstruction]]
) -> DataPack:
    """Delete the provided class relations from the provided data.

    Args:
        data:
            The data based on DataPack to delete the relations from.
        instructions_by_class:
            A dictionary mapping class names to lists of delete relation instructions.
    Returns:
        The data with the specified relations being deleted.
    """
    modified_data = data_to_dict(data)

    for class_name, instructions in instructions_by_class.items():
        class_resources = modified_data["resources"].get(class_name)

        if not class_resources:
            raise EvitableTransformationError()

        for resource in class_resources.values():
            for instruction in instructions:
                try:
                    del resource["relations"][instruction.relation_name]
                except KeyError as exc:
                    raise EvitableTransformationError() from exc

    return DataPack.model_validate(modified_data)
