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

"""Copy content properties between resources described by a relation path."""

from typing import Any

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.data_transform import transform_data
from metldata.builtin_transformations.copy_content.instruction import (
    CopyContentInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


def copy_content(
    *, data: DataPack, instructions_by_class: dict[str, list[CopyContentInstruction]]
):
    """Apply all transformation instructions."""
    return transform_data(
        data=data,
        instructions_by_class=instructions_by_class,
        calculate_value=values_to_copy,
    )


def values_to_copy(source_properties: list[Any]):
    """Return the single source property to be copied, ensuring no multiplicity."""
    num_source_properties = len(source_properties)
    # copy does not expect multiplicity along the given relation path
    # raise if this is assumption is violated here
    if num_source_properties > 1:
        raise EvitableTransformationError()
    elif num_source_properties == 0:
        # nothing to copy, move on to next resource
        # this should only happen if the property is optional and should be
        # caught by validating against the schemapack after transformation
        return

    return source_properties[0]
