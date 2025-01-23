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

"Common functions used in model transformations of individual transformations"

from schemapack.spec.schemapack import ClassDefinition, SchemaPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.common.instruction import TargetInstruction
from metldata.builtin_transformations.common.utils import content_to_dict, model_to_dict
from metldata.transform.exceptions import EvitableTransformationError


def update_model(
    *, model: SchemaPack, updated_class_defs: dict[str, ClassDefinition]
) -> SchemaPack:
    """Updates class definitions of a model that are subjected to model transformation"""
    model_dict = model_to_dict(model)
    model_dict["classes"].update(updated_class_defs)
    return SchemaPack.model_validate(model_dict)


def add_properties(
    *,
    model: SchemaPack,
    instructions_by_class: dict[str, list[TargetInstruction]],
    default_schema: dict,
) -> SchemaPack:
    """The target content - object_path(s) are added to the model with the
    'add_content_properties' step of the workflow. Thus, this function only adds the
    property_name(s) to the content schema of the classes that are subject to
    count_content_values transformation.
    """
    updated_class_defs: dict[str, ClassDefinition] = {}
    for class_name, cls_instructions in instructions_by_class.items():
        class_def = model.classes.get(class_name)

        if not class_def:
            raise EvitableTransformationError()

        content_schema = content_to_dict(class_def)

        for cls_instruction in cls_instructions:
            object_path = cls_instruction.target_content.object_path
            property_name = cls_instruction.target_content.property_name
            try:
                target_schema = resolve_schema_object_path(content_schema, object_path)
            except KeyError as exc:
                raise EvitableTransformationError() from exc

            if property_name in target_schema.get("properties", {}):
                raise EvitableTransformationError()

            target_schema.setdefault("properties", {})[property_name] = default_schema

        updated_class_defs[class_name] = class_def.model_validate(
            {**class_def.model_dump(), "content": content_schema}
        )
    return update_model(model=model, updated_class_defs=updated_class_defs)
