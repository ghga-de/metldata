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

"Assumptions for count references transformation"

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_schema_object_path,
)
from metldata.builtin_transformations.copy_content.instruction import (
    CopyContentInstruction,
)
from metldata.builtin_transformations.copy_content.path import (
    RelationPathGraph,
    RelationPathNode,
)
from metldata.transform.base import ModelAssumptionError


def check_model_assumptions(
    schema: SchemaPack,
    instructions_by_class: dict[str, list[CopyContentInstruction]],
) -> None:
    """Check the model assumptions for the count references transformation."""
    for _, instructions in instructions_by_class.items():
        for instruction in instructions:
            assert_relation_path_constraints(schema=schema, instruction=instruction)
            assert_source_and_property_exist(schema=schema, instruction=instruction)
            assert_target_content_exists(schema=schema, instruction=instruction)


def assert_relation_path_constraints(
    *, schema: SchemaPack, instruction: CopyContentInstruction
):
    """Assert that a relation path is parsable and fulfills the constraints, i.e.
    only one source and target are specified and the target is reachable from the source.
    """
    try:
        relations = RelationPathGraph(instruction.source.relation_path)
    except ValueError as exc:
        raise ModelAssumptionError(str(exc)) from exc

    for next_class, property in relations.first.points_to.items():
        _check_class_property_existence(
            schema=schema, node=next_class, property=property
        )


def _check_class_property_existence(
    *, schema: SchemaPack, node: RelationPathNode, property: str
):
    """Recursively check that classes and associated properties along a relation path do exist."""
    # check that the source class exists
    node_class = schema.classes.get(node.name)
    if not node_class:
        raise ModelAssumptionError(
            f"No class with name {node.name} present in the model, but specified in relation path."
        )

    # check associated property exists
    node_schema = node_class.content.json_schema_dict
    if not property in node_schema.get("properties", {}):
        raise ModelAssumptionError(
            f"No property with name {property} present for class {node.name} in the model, "
            "but specified in relation path."
        )

    for next_class, property in node.points_to.items():
        _check_class_property_existence(
            schema=schema, node=next_class, property=property
        )


def assert_source_and_property_exist(
    *, schema: SchemaPack, instruction: CopyContentInstruction
):
    """Check that both the source class and property exist."""
    relation_graph = RelationPathGraph(instruction.source.relation_path)
    source_class = relation_graph.last
    source_content_path = instruction.source.content_path

    # check that the source class exists
    source_class_def = schema.classes.get(source_class.name)
    if not source_class_def:
        raise ModelAssumptionError(
            f"No class with name {source_class.name} present in the model."
        )

    # check source content schema contains the given content path
    source_content_schema = source_class_def.content.json_schema_dict
    try:
        _ = resolve_schema_object_path(source_content_schema, source_content_path)
    except KeyError as exc:
        raise ModelAssumptionError(
            f"Could not find content path {source_content_path} within the {source_class.name} class."
        ) from exc


def assert_target_content_exists(
    *, schema: SchemaPack, instruction: CopyContentInstruction
):
    """Check that the target class exists and the property is not set yet."""
    target_property_name = instruction.target_content.property_name
    target_class = schema.classes.get(instruction.class_name)

    if not target_class:
        raise ModelAssumptionError(
            f"Target class {instruction.class_name} not present in model."
        )

    content_schema = target_class.content.json_schema_dict

    # check for property existence
    if target_property_name in content_schema.get("properties", {}):
        raise ModelAssumptionError(f"Property {target_property_name} already present.")
