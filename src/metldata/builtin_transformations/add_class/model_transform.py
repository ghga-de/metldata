# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Model transformation logic for the 'add class' transformation."""

from schemapack.spec.schemapack import (
    ClassDefinition,
    ClassRelation,
    IDSpec,
    SchemaPack,
)

from metldata.builtin_transformations.add_class.config import RelationSpec
from metldata.builtin_transformations.common.utils import model_to_dict


def add_model_class(  # noqa: PLR0913
    *,
    model: SchemaPack,
    class_name: str,
    id_property_name: str,
    content_schema: dict,
    description: str | None,
    relations: list[RelationSpec],
) -> SchemaPack:
    """Add a new class to the model."""
    new_class = ClassDefinition.model_validate(
        {
            "description": description,
            "id": IDSpec(propertyName=id_property_name),
            "content": content_schema,
            "relations": _build_relations(relations),
        }
    )

    model_dict = model_to_dict(model)
    model_dict["classes"][class_name] = new_class
    return SchemaPack.model_validate(model_dict)


def _build_relations(relations: list[RelationSpec]) -> dict[str, ClassRelation]:
    """Convert config relation specs into a dict of ClassRelation objects."""
    return {
        relation.relation_property_name: ClassRelation.model_validate(
            {
                "description": relation.description,
                "targetClass": relation.targetClass,
                "mandatory": relation.mandatory,
                "multiple": relation.multiple,
            }
        )
        for relation in relations
    }
