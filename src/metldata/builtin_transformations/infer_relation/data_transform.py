# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"Logic for transforming data."

from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.common.custom_types import (
    MutableClassResources,
    MutableDatapack,
)
from metldata.builtin_transformations.common.resolve_path.resolve_path_element_relations import (
    resolve_path,
)
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.infer_relation.config import (
    InferRelationConfig,
)
from metldata.transform.exceptions import EvitableTransformationError


def get_class_resources(
    *, data: MutableDatapack, class_name: str
) -> MutableClassResources:
    """Extract the resources of a given class from the dictionary."""
    resources = data["resources"].get(class_name)
    if not resources:
        raise EvitableTransformationError()
    return resources


def infer_data_relation(
    *, data: DataPack, transformation_config: InferRelationConfig
) -> DataPack:
    """Adds inferred relations to the data as given in the configuration."""
    modified_data = data_to_dict(data)

    # the target prefix refers to resources that will be modified by the transformation
    target_resources = get_class_resources(
        data=modified_data, class_name=transformation_config.class_name
    )

    path = transformation_config.relation_path
    referenced_class = path.target

    for resource_id, resource in target_resources.items():
        relation_target_ids = resolve_path(
            data=data, source_resource_id=resource_id, path=path
        )

        # add a new relation to that resource
        resource.setdefault("relations", {})[transformation_config.relation_name] = {
            "targetClass": referenced_class,
            "targetResources": relation_target_ids,
        }

    return DataPack.model_validate(modified_data)
