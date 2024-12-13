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
#

"""Logic for transforming data.

Here is a brief summary of the principle steps of transformation:
- iterate over inferred relations list from the config, per inferred relation:
    - extract the resources of the host class
    - iterate over host resources, per host resource:
        - iterate over path elements
            - iterate over source resources (for the first path element the host
              resource serves as the single source), per source resource:
                - resolve the path element for the source resource:
                    - if active reference:
                        - lookup target resources specified in the relation property
                          defined in the path element
                    - if passive reference:
                        - iterate over resources of the target class, per potential
                          target resource:
                            - if the resource references the source resource via the
                                relation property defined in the path element, add it to
                                the target resources of the path element in context of
                                the given source resource
            - collect the target resources for all source resources of the given path
              element
            - use the target resources of this iteration as the source resources for the
              next one
        - the target resources of the last path element are the target resources
          of the entire inferred relation for the given host resource
        - add the target resources to the host resource as a new relation property
          as defined in the inferred relation
"""

from schemapack.spec.custom_types import ResourceId
from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.common.path.path import (
    RelationPath,
)
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElement,
    RelationPathElementType,
)
from metldata.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
)
from metldata.transform.exceptions import EvitableTransformationError


def resolve_active_path_element(
    *,
    data: DataPack,
    source_resource_id: ResourceId,
    path_element: RelationPathElement,
) -> set[ResourceId] | frozenset[ResourceId]:
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
    target_resource_ids = source_resource.relations.get(path_element.property)
    if target_resource_ids is None:
        target_resource_ids = set()
    elif isinstance(target_resource_ids, str):
        target_resource_ids = {target_resource_ids}
    return target_resource_ids


def resolve_passive_path_element(
    *,
    data: DataPack,
    source_resource_id: ResourceId,
    path_element: RelationPathElement,
) -> set[ResourceId]:
    """Resolve the given relation inference path element of passive type for the given
    source resource.

    Args:
        data:
            The data pack to look up resources in.
        source_resource_id:
            The id of the resource to which the path element is applied.
        path_element:
            The relation inference path element to resolve. It is assumed to be of
            passive type.

    Returns:
        A set of resource IDs that are targeted by the path element in context of the
        given source resource.
    """
    if path_element.type_ != RelationPathElementType.PASSIVE:
        raise ValueError(
            "Expected path element of type 'PASSIVE', but got an 'ACTIVE' one."
        )
    candidate_resources = data.resources.get(path_element.target, {})
    target_resource_ids = set()

    for candidate_resource_id, candidate_resource in candidate_resources.items():
        relation = candidate_resource.relations.get(path_element.property, frozenset())
        if (
            isinstance(relation, frozenset) and source_resource_id in relation
        ) or source_resource_id == relation:
            target_resource_ids.add(candidate_resource_id)

    return target_resource_ids


def resolve_path_element(
    *,
    data: DataPack,
    source_resource_id: ResourceId,
    path_element: RelationPathElement,
) -> set[ResourceId] | frozenset[ResourceId]:
    """Resolve the given relation inference path element for the given source resource.

    Args:
        data: The data pack to look up resources in.
        source_resource_id: The id of the resource to which the path element is applied.
        path_element: The relation inference path element to resolve.

    Returns:
        A set of resource IDs that are targeted by the path element in context of the
        given source resource.
    """
    resolve = (
        resolve_active_path_element
        if path_element.type_ == RelationPathElementType.ACTIVE
        else resolve_passive_path_element
    )
    return resolve(
        data=data,
        source_resource_id=source_resource_id,
        path_element=path_element,
    )


def resolve_path(
    *, data: DataPack, source_resource_id: ResourceId, path: RelationPath
) -> set[ResourceId]:
    """Resolve the given relation inference path for the given source resource.

    Args:
        data: The data pack to look up resources in.
        source_resource_id: The id of the resource to which the path is applied.
        path: The relation inference path to resolve.

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
            for source_resource_id in resource_ids
            for target_resource_id in resolve_path_element(
                data=data,
                source_resource_id=source_resource_id,
                path_element=path_element,
            )
        }

    return resource_ids


def add_inferred_relations(
    *, data: DataPack, instructions: list[InferenceInstruction]
) -> DataPack:
    """Adds inferred relations to the given data as per the given instructions."""
    for instruction in instructions:
        host_resources = data.resources.get(instruction.source, {})
        updated_host_resources: dict[ResourceId, Resource] = {}

        for host_resource_id, host_resource in host_resources.items():
            target_resource_ids = resolve_path(
                data=data,
                source_resource_id=host_resource_id,
                path=instruction.path,
            )
            # transform into list (as references are stored as such) and make order
            # deterministic:
            updated_host_resources[host_resource_id] = host_resource.model_copy(
                update={
                    "relations": {
                        **host_resource.relations,
                        instruction.new_property: frozenset(
                            target_resource_ids
                        ),  # freeze inferred relations for datapack data type compatibility
                    }
                }
            )

        modified_data = data.model_copy(
            update={
                "resources": {
                    **data.resources,
                    instruction.source: updated_host_resources,
                }
            }
        )

    return modified_data
