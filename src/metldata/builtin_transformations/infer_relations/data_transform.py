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

from metldata.builtin_transformations.common.resolve_path import (
    resolve_path,
)
from metldata.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
)


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
                        instruction.new_property: target_resource_ids,
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
