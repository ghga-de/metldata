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
"""Model transformation logic for the 'count references' transformation"""

from copy import deepcopy

from schemapack.spec.schemapack import ClassDefinition, SchemaPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.copy_content.instruction import (
    CopyContentInstruction,
)
from metldata.builtin_transformations.copy_content.path import RelationPathGraph
from metldata.transform.base import EvitableTransformationError


def add_copy_content(
    *,
    model: SchemaPack,
    instructions_by_class: dict[str, list[CopyContentInstruction]],
) -> SchemaPack:
    """The target content - object_names are added to the model with the 'add_content_properties
    step of the workflow. Thus, this function only adds the property_name to a content schema.
    """
    updated_class: dict[str, ClassDefinition] = {}
    for class_name, instructions in instructions_by_class.items():
        target_class = model.classes.get(class_name)

        if not target_class:
            raise EvitableTransformationError()

        content_schema = target_class.content.json_schema_dict

        for instruction in instructions:
            # check for property existence
            target_property_name = instruction.target_content.property_name
            relation_graph = RelationPathGraph(instruction.source.relation_path)
            if target_property_name in content_schema.get("properties", {}):
                raise EvitableTransformationError()

            # extract schema information that needs to be copied
            source_class = relation_graph.last
            source_content_path = instruction.source.content_path

            # fetch property schema to copy
            source_class_def = model.classes.get(source_class.name)
            if not source_class_def:
                raise EvitableTransformationError()

            source_content_schema = source_class_def.content.json_schema_dict
            try:
                property_schema = resolve_schema_object_path(
                    source_content_schema, source_content_path
                )
            except KeyError as exc:
                raise EvitableTransformationError() from exc

            # add property schema to target class
            content_schema.setdefault("properties", {})[target_property_name] = (
                deepcopy(property_schema)
            )

        updated_class[class_name] = target_class.model_validate(
            {**target_class.model_dump(), "content": content_schema}
        )

    model_dict = model.model_dump()
    model_dict["classes"].update(updated_class)
    return SchemaPack.model_validate(model_dict)
