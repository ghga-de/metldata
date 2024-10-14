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

"""Logic for transforming data."""

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.copy_content.instruction import (
    CopyContentInstruction,
)
from metldata.builtin_transformations.copy_content.path import RelationPathGraph
from metldata.transform.base import EvitableTransformationError


def copy_content(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[CopyContentInstruction]],
) -> DataPack:
    """Given a data pack and a dictionary of instructions by class ...

    Args:
        data:
            The datapack to add the reference count values.
        instructions_by_class:
            A dictionary mapping class names to lists of instructions.

    Returns:
        ...
    """
    modified_data = data.model_copy(deep=True)
    for class_name, instructions in instructions_by_class.items():
        target_resources = modified_data.resources.get(class_name)

        if not target_resources:
            raise EvitableTransformationError()

        for target_resource in target_resources.values():
            for instruction in instructions:
                content = target_resource.content
                target_property_name = instruction.target_content.property_name
                relation_graph = RelationPathGraph(instruction.source.relation_path)

                if target_property_name in content:
                    raise EvitableTransformationError()
                source_resource_name = relation_graph.last.name

                # fetch property schema to copy
                source_resources = modified_data.resources.get(source_resource_name)
                if not source_resources:
                    raise EvitableTransformationError()

                if len(source_resources) != 1:
                    raise ValueError(
                        "Expected exactly one resource to copy from, but found multiple."
                    )
                source_resource = next(iter(source_resources.values()))

                source_content = source_resource.content
                for path_elem in instruction.source.content_path.split("."):
                    source_content = source_content.get(path_elem)
                    if not source_content:
                        raise EvitableTransformationError()

                content.setdefault("properties", {})[target_property_name] = (
                    source_content
                )

    return modified_data
