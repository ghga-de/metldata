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
from metldata.builtin_transformations.transform_content.config import (
    TransformContentConfig,
)
from metldata.transform.exceptions import EvitableTransformationError


def delete_data_class(
    *, data: DataPack, transformation_config: TransformContentConfig
) -> DataPack:
    """Delete class from the provided data."""
    modified_data = data_to_dict(data)


    return DataPack.model_validate(modified_data)
