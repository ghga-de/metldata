# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

from metldata.builtin_transformations.common.mutate import set_class_resources
from metldata.transform.exceptions import EvitableTransformationError


def duplicate_data_class(
    *, data: DataPack, source_class_name: str, target_class_name: str
) -> DataPack:
    """Copy the contents of a class in the given DataPack under a new class name.

    Args:
        data:
            The DataPack instance containing the source class to duplicate.
        transformation_config:
            Configuration specifying the source and target class for the copy operation.
    Returns:
        A new DataPack with the source class content duplicated under the target class name.
    """
    try:
        source_class_resources = data.resources[source_class_name]
    except KeyError as exc:
        raise EvitableTransformationError() from exc
    return set_class_resources(
        data=data, class_name=target_class_name, resources=source_class_resources
    )
