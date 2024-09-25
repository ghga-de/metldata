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

"""Data transformation logic for count content values transformation."""

from collections import Counter

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.path.path_utils import get_referred_class
from metldata.builtin_transformations.count_content_values.instruction import (
    CountContentValueInstruction,
)
from metldata.transform.exceptions import (
    EvitableTransformationError,
)


def count_content(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[CountContentValueInstruction]],
) -> DataPack:
    """Transforms the data."""
    modified_data = data.model_copy(deep=True)
    for class_name, instructions in instructions_by_class.items():
        resources = modified_data.resources.get(class_name)

        if not resources:
            raise EvitableTransformationError()

        for instruction in instructions:
            relation_path = instruction.source.relation_path
            referenced_class = get_referred_class(relation_path)

            # Only one element is expected in the path
            relation_name = relation_path.elements[0].property

            content_resources = modified_data.resources.get(referenced_class)

            if not content_resources:
                raise EvitableTransformationError()

            for resource in resources.values():
                content = resource.content
                related_to = resource.relations.get(relation_name)
                if not related_to:
                    raise EvitableTransformationError()

                try:
                    count_values = [
                        content_resources[relation].content.get(
                            instruction.source.content_path
                        )
                        for relation in related_to
                    ]
                except KeyError as exc:
                    raise EvitableTransformationError() from exc

                object = resolve_data_object_path(
                    data=content,
                    path=instruction.target_content.object_path,
                )
                if (
                    not isinstance(object, dict)
                    or instruction.target_content.property_name in object
                ):
                    raise EvitableTransformationError()

                object[instruction.target_content.property_name] = dict(
                    Counter(count_values)
                )

    return modified_data
