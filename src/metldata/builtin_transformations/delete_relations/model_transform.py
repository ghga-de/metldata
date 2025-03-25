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

"""Model transformation logic for the 'delete relations' transformation"""

from schemapack.spec.schemapack import ClassDefinition, SchemaPack

from metldata.builtin_transformations.common.model_transform import update_model
from metldata.builtin_transformations.common.utils import relations_to_dict
from metldata.builtin_transformations.delete_relations.instruction import (
    DeleteRelationInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


def delete_model_relations(
    *,
    model: SchemaPack,
    instructions_by_class: dict[str, list[DeleteRelationInstruction]],
) -> SchemaPack:
    """Delete relations from the model."""
    updated_class_defs: dict[str, ClassDefinition] = {}

    for class_name, instructions in instructions_by_class.items():
        class_def = model.classes.get(class_name)

        if not class_def:
            raise EvitableTransformationError()

        class_relations = relations_to_dict(class_def)

        for instruction in instructions:
            try:
                del class_relations[instruction.relation_name]
            except KeyError as exc:
                raise EvitableTransformationError() from exc

        updated_class_defs[class_name] = class_def.model_validate(
            {**class_def.model_dump(), "relations": class_relations}
        )

    return update_model(model=model, updated_class_defs=updated_class_defs)
