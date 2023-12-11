# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

from schemapack.spec.schemapack import (
    Cardinality,
    ClassDefinition,
    Relation,
    SchemaPack,
)
from schemapack.utils import FrozenDict

from metldata.schemapack_.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
)
from metldata.schemapack_.transform.base import EvitableTransformationError


def add_inferred_relations(
    *, model: SchemaPack, instructions: list[InferenceInstruction]
) -> SchemaPack:
    """Add inferred relations to a model.

    Args:
        model: The model based on SchemaPack to add the inferred relations to.
        instructions: The instructions for inferring relations.

    Returns:
        The model with the inferred relations added.
    """

    updated_class_defs: dict[str, ClassDefinition] = {}
    for instruction in instructions:
        class_def = (
            updated_class_defs[instruction.source]
            if instruction.source in updated_class_defs
            else model.classes.get(instruction.source)
        )

        if class_def is None:
            raise EvitableTransformationError()

        new_relation = Relation.model_validate(
            {
                "to": instruction.target,
                "cardinality": Cardinality.MANY_TO_MANY
                if instruction.allow_multiple
                else Cardinality.ONE_TO_MANY,
            }
        )
        updated_class_defs[instruction.source] = ClassDefinition.model_validate(
            {
                "id": class_def.id,
                "content": class_def.content,
                "relations": {
                    **class_def.relations,
                    instruction.new_property: new_relation,
                },
            }
        )

    return model.model_copy(
        update={"classes": FrozenDict({**model.classes, **updated_class_defs})}
    )
