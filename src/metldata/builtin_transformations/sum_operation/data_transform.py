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

"""Data transformation logic for sum operation transformation."""

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.data_transform import transform_data
from metldata.builtin_transformations.sum_operation.instruction import (
    SumOperationInstruction,
)


def sum_content(
    *, data: DataPack, instructions_by_class: dict[str, list[SumOperationInstruction]]
) -> DataPack:
    """Apply all transformation instructions."""
    return transform_data(
        data=data,
        instructions_by_class=instructions_by_class,
        calculate_value=sum,
    )
