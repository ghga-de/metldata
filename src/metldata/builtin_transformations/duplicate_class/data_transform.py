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
from metldata.builtin_transformations.duplicate_class.config import (
    DuplicateClassConfig,
)
from metldata.transform.exceptions import EvitableTransformationError


def duplicate_data_class(
    *, data: DataPack, transformation_config: DuplicateClassConfig
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

    source_class_name = transformation_config.source_class_name
    target_class_name = transformation_config.target_class_name
    try:
        source_class_resources = modified_data["resources"][source_class_name]
        # directly converted to a DataPack afterwards, no deep copy needed
        modified_data["resources"][target_class_name] = source_class_resources
    except KeyError as exc:
        raise EvitableTransformationError() from exc

    return DataPack.model_validate(modified_data)
