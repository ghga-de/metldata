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

from copy import deepcopy

from schemapack.spec.schemapack import (
    ClassDefinition,
    SchemaPack,
)

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.count_references.instruction import (
    AddReferenceCountPropertyInstruction,
)
from metldata.transform.base import EvitableTransformationError

# from metldata.transform.base import EvitableTransformationError


def add_count_references(
    *, model: SchemaPack, instructions_by_class: dict[str, list[AddReferenceCountPropertyInstruction]]
) -> SchemaPack:
    """Add a new content property (target_content) to the class(es) subject to
    transformation

    Args:
        model:
            The model based on SchemaPack to
    Returns:
        The model with the
    """
    # TODO model transform logic for count references
    updated_class_defs: dict[str, ClassDefinition] = {}
    for class_name, cls_instructions in instructions_by_class.items():
        for class_name, cls_instructions in instructions_by_class.items():
            class_def = model.classes.get(class_name)

            if not class_def:
                raise EvitableTransformationError()

            content_schema = class_def.content.json_schema_dict

            for cls_instruction in cls_instructions:
                try:
                    target_object = resolve_schema_object_path(
                        content_schema, cls_instruction.target_content.object_path
                    )
                except KeyError as e:
                    raise EvitableTransformationError() from e

                if cls_instruction.target_content.property_name in content_schema.get(
                    "properties", {}
                ):
                    raise EvitableTransformationError()

                target_object.setdefault("properties", {})[
                    cls_instruction.target_content.property_name
                ] = deepcopy(cls_instruction.content_schema)
    return model
