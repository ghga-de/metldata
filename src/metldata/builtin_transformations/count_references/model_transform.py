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
"""Model transformation logic for the 'count references' transformation"""

from schemapack.spec.schemapack import (
    SchemaPack,
)

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)
from metldata.transform.base import EvitableTransformationError


def add_count_references(
    *,
    model: SchemaPack,
    instructions_by_class: dict[str, list[AddReferenceCountPropertyInstruction]],
) -> SchemaPack:
    """The content properties are added to the model with the 'add_content_properties
    step of the workflow. Thus, this function applies no transformation.
    It only checks for EvitableTransformationError.
    """
    for class_name, cls_instructions in instructions_by_class.items():
        class_def = model.classes.get(class_name)

        if not class_def:
            raise EvitableTransformationError()

        content_schema = class_def.content.json_schema_dict

        for cls_instruction in cls_instructions:
            try:
                resolve_schema_object_path(
                    content_schema, cls_instruction.target_content.object_path
                )
            except KeyError as e:
                raise EvitableTransformationError() from e

            if cls_instruction.target_content.property_name in content_schema.get(
                "properties", {}
            ):
                raise EvitableTransformationError()
    return model
