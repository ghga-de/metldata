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
#

"""Logic for transforming metadata models."""

from schemapack.spec.schemapack import (
    ClassDefinition,
    MandatoryRelationSpec,
    MultipleRelationSpec,
    Relation,
    SchemaPack,
)

from metldata.builtin_transformations.infer_relations.path.path import RelationPath
from metldata.builtin_transformations.infer_relations.path.path_elements import (
    RelationPathElement,
    RelationPathElementType,
)
from metldata.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
)
from metldata.transform.base import EvitableTransformationError


def get_relation(element: RelationPathElement, schema: SchemaPack) -> Relation:
    """Get the relation object for a path element.

    Args:
        element: The path element to get the relation for.
        schema: The underlying schema.

    Returns:
        The relation object.
    """
    element_active = element.type_ == RelationPathElementType.ACTIVE
    class_name = element.source if element_active else element.target
    return schema.classes[class_name].relations[element.property]


def infer_mutiplicity_from_path(
    path: RelationPath, schema: SchemaPack
) -> MultipleRelationSpec:
    """Infer the multiplicity of an inferred relation based on the path.

    Args:
        path: The path to infer the multiplicity for.
        schema: The underlying schema.

    Returns:
        The inferred multiplicity.
    """
    origin = target = False
    # Traverse the path and check for multiplicity
    for element in path.elements:
        relation = get_relation(element, schema)
        # If any multiplicity is observed, toggle the origin / source flag depending on
        # the orientation of the relation.
        if element.type_ == RelationPathElementType.ACTIVE:
            if relation.multiple.origin:
                origin = True
            if relation.multiple.target:
                target = True
        else:
            if relation.multiple.origin:
                target = True
            if relation.multiple.target:
                origin = True
        if origin and target:
            break
    return MultipleRelationSpec(origin=origin, target=target)


def infer_mandatory_from_path(
    path: RelationPath, schema: SchemaPack
) -> MandatoryRelationSpec:
    """Infer the mandatory property of an inferred relation based on the path.

    Args:
        path: The path to infer the mandatory property for.
        schema: The underlying schema.

    Returns:
        The inferred mandatory property.
    """
    origin = target = True
    # Traverse the path and check for mandatory
    for element in path.elements:
        relation = get_relation(element, schema)
        # If either end is not mandatory, toggle the origin / source flag depending on
        # the orientation of the relation.
        if element.type_ == RelationPathElementType.ACTIVE:
            if not relation.mandatory.origin:
                origin = False
            if not relation.mandatory.target:
                target = False
        else:
            if not relation.mandatory.origin:
                target = False
            if not relation.mandatory.target:
                origin = False
        if not origin and not target:
            break
    return MandatoryRelationSpec(origin=origin, target=target)


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

        mandatory = infer_mandatory_from_path(instruction.path, model)
        multiple = infer_mutiplicity_from_path(instruction.path, model)
        new_relation = Relation.model_validate(
            {
                "targetClass": instruction.target,
                "mandatory": mandatory,
                "multiple": multiple,
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

    model_dict = model.model_dump()
    model_dict["classes"].update(updated_class_defs)
    return SchemaPack.model_validate(model_dict)
