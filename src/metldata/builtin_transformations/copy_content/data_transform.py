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

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.resolve_path import resolve_path
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.copy_content.instruction import (
    CopyContentInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


def copy_content(
    *,
    data: DataPack,
    instructions_by_class: dict[str, list[CopyContentInstruction]],
) -> DataPack:
    """Copy content properties between resources described by a relation path."""
    modified_data = data_to_dict(data)
    resources = modified_data["resources"]

    for class_name, instructions in instructions_by_class.items():
        # Check resources exist for class to be modified
        target_resources = resources.get(class_name)
        if not target_resources:
            raise EvitableTransformationError()

        for instruction in instructions:
            relation_path = instruction.source.relation_path
            content_path = instruction.source.content_path
            property_name = instruction.target_content.property_name

            source_class_name = relation_path.target
            source_resources = resources.get(source_class_name)

            # handle copying for each resource that should be modified
            for resource_id in target_resources:
                source_resource_ids = resolve_path(
                    data=data, source_resource_id=resource_id, path=relation_path
                )

                num_source_resources = len(source_resource_ids)
                # copy does not expect multiplicity along the given relation path
                # raise if this is assumption is violated here
                if num_source_resources > 1:
                    raise EvitableTransformationError()
                elif num_source_resources == 0:
                    # nothing to copy, move on to next resource
                    # TODO: this should probably differentiate between required and not
                    # required properties, but would need schema introspection to do that
                    continue

                # exactly one value in the frozenset, so unpacking this way works
                (source_resource_id,) = source_resource_ids
                source_resource = source_resources[source_resource_id]

                source_property = resolve_data_object_path(
                    source_resource.content, path=content_path
                )
                target_resource = target_resources[resource_id]

                # the target property should not be present in the resource
                # of the class that's being modified
                if target_resource.content.get(property_name):
                    raise EvitableTransformationError()

                # TODO: default placheholder for now, needs better code here
                # not sure if this would also need schema introspection or all cases
                # can be enumerated exhaustively
                target_resource.content.setdefault(
                    property_name, type(source_property)()
                )
                ...

    return data
