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

from metldata.builtin_transformations.common.utils import thaw_frozen_dict
from metldata.transform.exceptions import EvitableTransformationError


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
    updated_classes: dict = {}

    for class_name, properties in properties_by_class.items():
        class_resources = data.resources.get(class_name)

        if not class_resources:
            raise EvitableTransformationError()
        
        # convert to a mutable dict to modify it
        # note that, it does not apply mutability to inner layer Resource objects
        mutable_class_resources = thaw_frozen_dict(class_resources)

        for resource_id, resource in class_resources.items():
            # convert to a mutable dict to modify it in place
            resource_content = thaw_frozen_dict(resource.content)
            for property in properties:
                resource_content.pop(property, None)
            mutable_class_resources[resource_id] = resource.model_copy(
                update={"content": resource_content}
            )
        updated_classes[class_name]= class_resources.update(mutable_class_resources)
    updated_resources = data.resources.update(updated_classes)
    modified_data = data.model_copy(update={"resources": updated_resources})
    return modified_data
