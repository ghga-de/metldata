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

"Combines functions controlling source-instruction dependent common assumptions."

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.instruction import (
    InstructionProtocol,
    SourceInstructionProtocol,
)
from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.transform.exceptions import ModelAssumptionError


def assert_class_is_source(
    *, path: RelationPath, instruction: InstructionProtocol
) -> None:
    """Validate that the class being modified matches the class specified in the
    relation path.
    """
    class_to_modify = instruction.class_name
    if path.source != class_to_modify:
        raise ModelAssumptionError(
            f"Class {class_to_modify} is not the source of the given relation path "
            f"{path}."
        )


def assert_source_content_path_exists(
    *, schema: SchemaPack, instruction: SourceInstructionProtocol
) -> None:
    """Ensure that the slot given as 'content path' of an instruction source
    exists in the content schema of the class that is referred in the 'relation path'.
    """
    path = instruction.source.relation_path
    content_path = instruction.source.content_path

    referenced_class = path.target

    class_def = schema.classes.get(referenced_class)

    if not class_def:
        raise ModelAssumptionError(
            f"Class {referenced_class} does not exist in the model."
        )

    content_slot = class_def.content["properties"].get(content_path)

    if not content_slot:
        raise ModelAssumptionError(
            f"Class {referenced_class} does not have {content_path} in its content"
            + " schema."
        )
