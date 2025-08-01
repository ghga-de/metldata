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

"""Data transformation logic for the 'delete class' transformation"""

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.transform.exceptions import EvitableTransformationError


def delete_data_class(*, data: DataPack, class_name: str) -> DataPack:
    """Delete class from the provided data."""
    modified_data = data_to_dict(data)

    try:
        del modified_data["resources"][class_name]
    except KeyError as exc:
        raise EvitableTransformationError() from exc

    _remove_relations_from_data(
        modified_data=modified_data,
        original_data=data,
        target_class=class_name,
    )
    return DataPack.model_validate(modified_data)


def _remove_relations_from_data(
    *, modified_data: dict, original_data: DataPack, target_class: str
) -> None:
    """Remove relations associated to deleted class from the data.

    Args:
        modified_data (dict): Dictionary representation of the data
        original_data (DataPack): Original data
        target_class (str): Name of the class to be deleted
    """
    for class_name, class_resources in original_data.resources.items():
        if class_name == target_class:
            continue

        for resource_id, resource in class_resources.items():
            filtered_relations = {
                name: specification
                for name, specification in resource.relations.items()
                if specification.targetClass != target_class
            }
            modified_data["resources"][class_name][resource_id]["relations"] = (
                filtered_relations
            )
