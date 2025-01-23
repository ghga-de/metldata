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

"""data transform"""

from collections import Counter

from schemapack._internals.spec.custom_types import ResourceId
from schemapack._internals.spec.datapack import ResourceIdSet
from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.add_content_properties.path import (
    resolve_data_object_path,
)
from metldata.builtin_transformations.common.custom_types import (
    MutableClassResources,
    MutableDatapack,
    MutableResource,
    MutableResourceContent,
    ResolveRelations,
)
from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.resolve_path import resolve_path
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.count_content_values.instruction import (
    CountContentValueInstruction,
)
from metldata.builtin_transformations.sum_operation.instruction import (
    SumOperationInstruction,
)
from metldata.transform.exceptions import (
    EvitableTransformationError,
)


def sum_content(
    *, data: DataPack, instructions_by_class: dict[str, list[SumOperationInstruction]]
) -> DataPack:
    """TODO"""
    return data


def transform_resource(
    *,
    referenced_resources: MutableClassResources,
    target_resource: MutableResource,
    relation_target_ids: frozenset[str],
    instruction: CountContentValueInstruction,
):
    """Apply the count content value transformation to each resource of a class."""
    target_content = target_resource.get("content")
    if target_content is None:
        raise EvitableTransformationError()

    values_to_count = get_values_to_count(
        relation_target_ids=relation_target_ids,
        referenced_resources=referenced_resources,
        content_path=instruction.source.content_path,
    )
    target_object = get_modification_target(
        data=target_content, instruction=instruction
    )
    target_property = instruction.target_content.property_name
    target_object[target_property] = dict(Counter(values_to_count))


def get_values_to_count(
    *,
    relation_target_ids: ResourceId | ResourceIdSet,
    referenced_resources: MutableClassResources,
    content_path: str,
):
    """Get countable properties from all resources referred to by the relation."""
    try:
        return [
            referenced_resources[resource_id]["content"].get(content_path)
            for resource_id in relation_target_ids
        ]
    except KeyError as exc:
        raise EvitableTransformationError() from exc


def get_modification_target(
    *, data: MutableResourceContent, instruction: CountContentValueInstruction
):
    """Get the json object that is to be modified."""
    path = instruction.target_content.object_path
    property = instruction.target_content.property_name

    target = resolve_data_object_path(data=data, path=path)
    if not isinstance(target, dict) or property in target:
        raise EvitableTransformationError()
    return target
