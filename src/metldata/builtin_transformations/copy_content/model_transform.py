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

"""Copy (sub)schemas of content properties between classes described by a relation path."""

from schemapack.spec.schemapack import ClassDefinition, SchemaPack

from metldata.builtin_transformations.common.model_transform import (
    add_property_per_instruction,
    resolve_schema_object_path,
    update_model,
)
from metldata.builtin_transformations.common.utils import content_to_dict
from metldata.builtin_transformations.copy_content.instruction import (
    CopyContentInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


def add_content_schema_copy(
    *,
    model: SchemaPack,
    instructions_by_class: dict[str, list[CopyContentInstruction]],
) -> SchemaPack:
    """Modify model to incorporate content (sub)schemas from copy source into the target class."""
    updated_class_defs: dict[str, ClassDefinition] = {}

    for class_name, instructions in instructions_by_class.items():
        class_def = model.classes.get(class_name)
        if not class_def:
            raise EvitableTransformationError()
        content_schema = content_to_dict(class_def)

        for instruction in instructions:
            relation_path = instruction.source.relation_path
            content_path = instruction.source.content_path

            # resolve content subschema to copy
            source_class_def = model.classes.get(relation_path.target)
            if not source_class_def:
                raise EvitableTransformationError()
            source_class_schema = content_to_dict(source_class_def)
            try:
                source_content_schema = resolve_schema_object_path(
                    source_class_schema, content_path
                )
            except KeyError as exc:
                raise EvitableTransformationError() from exc

            add_property_per_instruction(
                cls_instruction=instruction,
                content_schema=content_schema,
                source_schema=source_content_schema,
            )

        updated_class_defs[class_name] = class_def.model_validate(
            {**class_def.model_dump(), "content": content_schema}
        )
    return update_model(model=model, updated_class_defs=updated_class_defs)
