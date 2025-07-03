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

"Model transformation logic for the 'merge relations' transformation"

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.custom_types import MutableClassRelations
from metldata.builtin_transformations.common.utils import model_to_dict
from metldata.builtin_transformations.merge_relations.config import MergeRelationsConfig
from metldata.transform.exceptions import EvitableTransformationError


def merge_model_relations(
    *, model: SchemaPack, transformation_config: MergeRelationsConfig
) -> SchemaPack:
    """Model transformation logic for the 'merge relations' transformation"""
    mutable_model = model_to_dict(model)

    class_name = transformation_config.class_name
    target_relation_name = transformation_config.target_relation
    source_relations = transformation_config.source_relations

    target_class = _get_target_class(
        model=model, class_name=class_name, source_relations=source_relations
    )

    try:
        mutable_class_relations = mutable_model["classes"][class_name]["relations"]
    except KeyError as exc:
        raise EvitableTransformationError from exc

    # add the new relation
    mutable_class_relations[target_relation_name] = {
        "targetClass": target_class,
        "mandatory": transformation_config.mandatory,
        "multiple": transformation_config.multiple,
        "description": transformation_config.description,
    }

    # delete relations that are merged
    _delete_relations_from_model(
        class_relations=mutable_class_relations, source_relations=source_relations
    )

    return SchemaPack.model_validate(mutable_model)


def _get_target_class(
    *, model: SchemaPack, class_name: str, source_relations: list[str]
) -> str:
    """Retrieve the target class name from the first relation in given in 'source relations'."""
    class_definition = model.classes.get(class_name)

    if class_definition is None:
        raise EvitableTransformationError()

    class_relations = class_definition.relations.get(source_relations[0])

    if class_relations is None:
        raise EvitableTransformationError()

    return class_relations.targetClass


def _delete_relations_from_model(
    *, class_relations: MutableClassRelations, source_relations: list[str]
) -> None:
    """Delete the relations specified in 'source relations' from the class_relations."""
    for relation_name in source_relations:
        try:
            del class_relations[relation_name]
        except KeyError as exc:
            raise EvitableTransformationError from exc
