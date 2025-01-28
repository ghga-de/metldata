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

"""Copy (sub)schemas of content properties between classes described by a relation path."""

from schemapack.spec.schemapack import ClassDefinition, SchemaPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.common.model_transform import update_model
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
        target_class_def = model.classes.get(class_name)

        if not target_class_def:
            raise EvitableTransformationError()

        target_content_schema = content_to_dict(target_class_def)
        for instruction in instructions:
            relation_path = instruction.source.relation_path

            # fetch class to copy content from
            source_class_def = model.classes.get(relation_path.target)
            if not source_class_def:
                raise EvitableTransformationError()
            source_class_schema = content_to_dict(source_class_def)

            # resolve content subschema to copy
            content_path = instruction.source.content_path
            try:
                source_content_schema = resolve_schema_object_path(
                    source_class_schema, content_path
                )
            except KeyError as exc:
                raise EvitableTransformationError() from exc

            # sanity check if property already exists at target class
            property_name = instruction.target_content.property_name
            object_path = instruction.target_content.object_path

            target_schema = resolve_schema_object_path(
                target_content_schema, object_path
            )

            if property_name in target_schema.get("properties", {}):
                raise EvitableTransformationError()

            # set content subschema for the selected property
            target_schema.setdefault("properties", {})[property_name] = (
                source_content_schema
            )

        updated_class_defs[class_name] = target_class_def.model_validate(
            {**target_class_def.model_dump(), "content": target_content_schema}
        )

    return update_model(model=model, updated_class_defs=updated_class_defs)
