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

from schemapack.spec.datapack import DataPack

from metldata.transform.base import EvitableTransformationError


def delete_properties(
    *, data: DataPack, properties_by_class: dict[str, list[str]]
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
    modified_data = data.model_copy(deep=True)

    for class_name, properties in properties_by_class.items():
        resources = modified_data.resources.get(class_name)

        if not resources:
            raise EvitableTransformationError()

        for resource in resources.values():
            for property in properties:
                resource.content.pop(property, None)

    return modified_data