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

"Resolve relation paths (active, passive and complex) and infer target resources of the overall path."

from schemapack.spec.custom_types import ResourceId
from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.custom_types import (
    PassiveIndex,
    PassiveIndexes,
)
from metldata.builtin_transformations.common.path import (
    RelationPath,
)
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElement,
    RelationPathElementType,
)
from metldata.transform.exceptions import EvitableTransformationError


def resolve_active_path_element(
    *,
    data: DataPack,
    source_resource_id: ResourceId,
    path_element: RelationPathElement,
) -> frozenset[ResourceId]:
    """Resolve the given relation inference path element of active type for the given
    source resource.

    Args:
        data:
            The data pack to look up resources in.
        source_resource_id:
            The id of the resource to which the path element is applied.
        path_element:
            The relation inference path element to resolve. It is assumed to be of
            active type.

    Returns:
        A set of resource IDs that are targeted by the path element in context of the
        given source resource.
    """
    if path_element.type_ != RelationPathElementType.ACTIVE:
        raise ValueError(
            "Expected path element of type 'ACTIVE', but got a 'PASSIVE' one."
        )

    source_resource = data.resources.get(path_element.source, {}).get(
        source_resource_id
    )

    if not source_resource:
        raise EvitableTransformationError()
    target_resource_relations = source_resource.relations.get(path_element.property)
    target_resource_ids = (
        target_resource_relations.targetResources
        if target_resource_relations
        else frozenset()
    )
    if target_resource_ids is None:
        target_resource_ids = frozenset()
    elif isinstance(target_resource_ids, str):
        target_resource_ids = frozenset({target_resource_ids})
    return target_resource_ids


def build_passive_index(
    *, data: DataPack, path_element: RelationPathElement
) -> PassiveIndex:
    """Build a reverse index for a single passive path element in one pass.

    A passive element answers the question "which resources reference me?". It walks the target
    class a single time and records, for every referenced id, the set of resources that
    reference it.

    Args:
        data:
            The data pack to look up resources in.
        path_element:
            The relation inference path element to index. It is assumed to be of
            passive type.

    Returns:
        A mapping from each referenced (source) resource id to the set of resource ids
        of ``path_element.target`` that reference it via ``path_element.property``.
    """
    if path_element.type_ != RelationPathElementType.PASSIVE:
        raise ValueError(
            "Expected path element of type 'PASSIVE', but got an 'ACTIVE' one."
        )

    index: PassiveIndex = {}
    candidate_resources = data.resources.get(path_element.target, {})

    for candidate_resource_id, candidate_resource in candidate_resources.items():
        candidate_resource_relations = candidate_resource.relations.get(
            path_element.property
        )
        if not candidate_resource_relations:
            continue

        target_resources = candidate_resource_relations.targetResources
        if target_resources is None:
            continue
        if isinstance(target_resources, str):
            target_resources = (target_resources,)

        for referenced_id in target_resources:
            index.setdefault(referenced_id, set()).add(candidate_resource_id)

    return index


def build_passive_indexes(*, data: DataPack, path: RelationPath) -> PassiveIndexes:
    """Build reverse indexes for all passive elements of a path.
    The indexes are built once and reused for every source resource.

    Args:
        data: The data pack to look up resources in.
        path: The relation inference path whose passive elements are indexed.

    Returns:
        A mapping from each passive element's ``(target class, property)`` pair to its
        reverse index. Active elements are omitted.
    """
    return {
        (element.target, element.property): build_passive_index(
            data=data, path_element=element
        )
        for element in path.elements
        if element.type_ == RelationPathElementType.PASSIVE
    }


def resolve_passive_path_element(
    *,
    source_resource_id: ResourceId,
    passive_index: PassiveIndex,
) -> frozenset[ResourceId]:
    """Resolve the given relation inference path element of passive type for the given
    source resource using a precomputed reverse index.

    Args:
        source_resource_id:
            The id of the resource to which the path element is applied.
        passive_index:
            The reverse index of the passive path element, as produced by
            :func:`build_passive_index`.

    Returns:
        A set of resource IDs that are targeted by the path element in context of the
        given source resource.
    """
    return frozenset(passive_index.get(source_resource_id, frozenset()))


def resolve_path_element(
    *,
    data: DataPack,
    source_resource_id: ResourceId,
    path_element: RelationPathElement,
    passive_index: PassiveIndex | None,
) -> frozenset[ResourceId]:
    """Resolve the given relation inference path element for the given source resource.

    Args:
        data: The data pack to look up resources in.
        source_resource_id: The id of the resource to which the path element is applied.
        path_element: The relation inference path element to resolve.
        passive_index:
            The reverse index for the element if it is passive, otherwise ``None``.

    Returns:
        A set of resource IDs that are targeted by the path element in context of the
        given source resource.
    """
    if path_element.type_ == RelationPathElementType.ACTIVE:
        return resolve_active_path_element(
            data=data,
            source_resource_id=source_resource_id,
            path_element=path_element,
        )

    if passive_index is None:
        raise EvitableTransformationError()
    return resolve_passive_path_element(
        source_resource_id=source_resource_id,
        passive_index=passive_index,
    )


def resolve_path(
    *,
    data: DataPack,
    source_resource_id: ResourceId,
    path: RelationPath,
    passive_indexes: PassiveIndexes,
) -> frozenset[ResourceId]:
    """Resolve the given relation inference path for the given source resource.

    Args:
        data: The data pack to look up resources in.
        source_resource_id: The id of the resource to which the path is applied.
        path: The relation inference path to resolve.
        passive_indexes:
            Reverse indexes for the passive elements of ``path``, keyed by their
            ``(target class, property)`` pair, as produced by
            :func:`build_passive_indexes`.

    Returns:
        A set of resource IDs that are targeted by the path in context of the given
        source resource.
    """
    resource_ids: set[ResourceId] = {source_resource_id}
    for path_element in path.elements:
        # the target resources of the current iteration are the source resources of the
        # next iteration:
        resource_ids = {
            target_resource_id
            for current_source_id in resource_ids
            for target_resource_id in resolve_path_element(
                data=data,
                source_resource_id=current_source_id,
                path_element=path_element,
                passive_index=passive_indexes.get(
                    (path_element.target, path_element.property)
                ),
            )
        }
    return frozenset(resource_ids)
