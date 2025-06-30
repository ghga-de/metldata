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

"Model transformation logic for the 'infer relation' transformation"

from schemapack.spec.schemapack import (
    ClassDefinition,
    ClassRelation,
    MandatoryRelationSpec,
    MultipleRelationSpec,
    SchemaPack,
)

from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)
from metldata.builtin_transformations.common.utils import get_relation, model_to_dict
from metldata.builtin_transformations.infer_relation.config import InferRelationConfig
from metldata.transform.exceptions import EvitableTransformationError


def infer_multiplicity_from_path(
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


def infer_model_relation(
    *, model: SchemaPack, transformation_config: InferRelationConfig
) -> SchemaPack:
    """Add inferred relations to a model.

    Args:
        model: The model based on SchemaPack to add the inferred relations to.
        transformation_config: The config for inferring relations.

    Returns:
        The model with the inferred relation added.
    """
    updated_class_def: dict[str, ClassDefinition] = {}

    path = transformation_config.relation_path

    # This is the class that is being modified
    source_class = transformation_config.relation_path.source

    # This is the class that is referred by the path
    target_class = transformation_config.relation_path.target

    class_def = model.classes.get(source_class)

    if class_def is None:
        raise EvitableTransformationError()

    mandatory = infer_mandatory_from_path(path, model)
    multiple = infer_multiplicity_from_path(path, model)
    new_relation = ClassRelation.model_validate(
        {
            "targetClass": target_class,
            "mandatory": mandatory,
            "multiple": multiple,
        }
    )
    updated_class_def[source_class] = ClassDefinition.model_validate(
        {
            "id": class_def.id,
            "content": class_def.content,
            "relations": {
                **class_def.relations,
                transformation_config.relation_name: new_relation,
            },
        }
    )

    model_dict = model_to_dict(model)
    model_dict["classes"].update(updated_class_def)
    return SchemaPack.model_validate(model_dict)
