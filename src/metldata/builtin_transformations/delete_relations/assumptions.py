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

"Assumptions for delete reference transformation"

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions.path_assumptions import (
    check_class_exists,
    check_relation_exists,
)
from metldata.builtin_transformations.delete_relations.instruction import (
    DeleteRelationInstruction,
)


def check_model_assumptions(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[DeleteRelationInstruction]],
) -> None:
    """Check model assumptions for the delete reference transformation."""
    for _, instructions in instructions_by_class.items():
        for instruction in instructions:
            check_class_exists(model=schema, class_name=instruction.class_name)
            check_relation_exists(
                model=schema,
                class_name=instruction.class_name,
                relation=instruction.relation_name,
            )
