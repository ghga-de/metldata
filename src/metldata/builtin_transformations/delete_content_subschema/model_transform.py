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
#

"""Logic for transforming metadata models."""

from contextlib import suppress

from schemapack.spec.schemapack import (
    ClassDefinition,
    SchemaPack,
)

from metldata.builtin_transformations.common.model_transform import (
    resolve_schema_object_path,
    update_model,
)
from metldata.builtin_transformations.common.utils import content_to_dict
from metldata.builtin_transformations.delete_content_subschema.instruction import (
    DeleteContentSubschemaInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


def delete_content_subschema(
    *,
    model: SchemaPack,
    instructions_by_class: dict[str, list[DeleteContentSubschemaInstruction]],
) -> SchemaPack:
    """Delete content properties from a model.

    Args:
        model:
            The model based on SchemaPack to delete the content properties from.
        properties_by_class:
            A dictionary mapping class names to lists of content properties to delete.

    Returns:
        The model with the specified content properties being deleted.
    """
    updated_class_defs: dict[str, ClassDefinition] = {}
    for class_name, instructions in instructions_by_class.items():
        class_def = model.classes.get(class_name)

        if not class_def:
            raise EvitableTransformationError()

        content_schema = content_to_dict(class_def)

        for instruction in instructions:
            content_path = instruction.content_path
            target_schema = content_schema

            # resolve is one layer to deep, go one step up in content path
            path_parent, _, target_property = content_path.rpartition(".")

            if path_parent:
                target_schema = resolve_schema_object_path(content_schema, path_parent)

            del target_schema["properties"][target_property]
            if "required" in target_schema:
                with suppress(ValueError):
                    target_schema["required"].remove(target_property)
                # if no required properties are left, remove the list
                if len(target_schema["required"]) == 0:
                    del target_schema["required"]

        updated_class_defs[class_name] = class_def.model_validate(
            {**class_def.model_dump(), "content": content_schema}
        )

    return update_model(model=model, updated_class_defs=updated_class_defs)
