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

"""Copy content properties between resources described by a relation path."""

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.custom_types import (
    MutableClassResources,
    MutableResource,
    ResourceId,
)
from metldata.builtin_transformations.common.resolve_path import resolve_path
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.copy_content.instruction import (
    CopyContentInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


class ContentCopier:
    """Helper for content copying."""

    def __init__(
        self,
        *,
        data: DataPack,
        instructions_by_class: dict[str, list[CopyContentInstruction]],
    ):
        self.instructions_by_class = instructions_by_class
        self.data = data
        self.modified_data = data_to_dict(self.data)
        self.resources = self.modified_data["resources"]

    def process_instructions(self):
        """Process high-level checks and delegate instruction processing."""
        for class_name, instructions in self.instructions_by_class.items():
            # Check resources exist for class to be modified
            target_resources = self.resources.get(class_name)
            if not target_resources:
                raise EvitableTransformationError()

            for instruction in instructions:
                self.process_instruction(
                    target_resources=target_resources, instruction=instruction
                )

        return DataPack.model_validate(self.modified_data)

    def process_instruction(
        self,
        target_resources: MutableClassResources,
        instruction: CopyContentInstruction,
    ):
        """Delegate copying for each resource that should be modified."""
        source_class_name = instruction.source.relation_path.target
        source_resources = self.resources.get(source_class_name)
        if not source_resources:
            raise EvitableTransformationError()

        for resource_id in target_resources:
            self.modify_resource(
                instruction=instruction,
                resource_id=resource_id,
                source_resources=source_resources,
                target_resources=target_resources,
            )

    def modify_resource(
        self,
        *,
        instruction: CopyContentInstruction,
        resource_id: ResourceId,
        source_resources: MutableClassResources,
        target_resources: MutableClassResources,
    ):
        """Copy content from source to target resource."""
        content_path = instruction.source.content_path
        relation_path = instruction.source.relation_path
        property_name = instruction.target_content.property_name

        source_resource_ids = resolve_path(
            data=self.data, source_resource_id=resource_id, path=relation_path
        )
        num_source_resources = len(source_resource_ids)
        # copy does not expect multiplicity along the given relation path
        # raise if this is assumption is violated here
        if num_source_resources > 1:
            raise EvitableTransformationError()
        elif num_source_resources == 0:
            # nothing to copy, move on to next resource
            # this should only happen if the property is optional and should be
            # caught by validating against the schemapack after transformation
            return

        # exactly one value in the frozenset, so unpacking this way works
        (source_resource_id,) = source_resource_ids
        source_resource = source_resources[source_resource_id]

        source_property = resolve_data_object_path(
            source_resource["content"], path=content_path
        )
        target_resource: MutableResource = target_resources[resource_id]
        # the target property should not be present in the resource
        # of the class that's being modified
        if target_resource["content"].get(property_name):
            raise EvitableTransformationError()

        target_resource["content"][property_name] = source_property
