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

"""Data transformation logic for the 'replace resource ids' transformation"""

from arcticfreeze import FrozenDict
from pydantic import BaseModel
from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.common.custom_types import (
    AccessionMap,
    MutableDatapack,
    ResourceId,
)
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.transform.exceptions import EvitableTransformationError


def replace_data_resource_ids(
    *,
    data: DataPack,
    class_name: str,
    annotation: BaseModel,
) -> DataPack:
    """Replace resource ids of a data class using annotations."""
    modified_data = data_to_dict(data)

    resource_accessions = _get_resource_accessions(
        annotation=annotation, class_name=class_name
    )

    original_resources = data.resources.get(class_name)
    if original_resources is None:
        raise EvitableTransformationError()

    updated_resources = _update_resources(
        original_resources=original_resources,
        resource_accessions=resource_accessions,
        class_name=class_name,
    )

    modified_data["resources"][class_name] = updated_resources

    _replace_ids_in_relations(
        modified_data=modified_data,
        original_data=data,
        target_class=class_name,
        resource_accessions=resource_accessions,
    )
    return DataPack.model_validate(modified_data)


def _get_resource_accessions(*, class_name: str, annotation: BaseModel) -> AccessionMap:
    """Extract resource ids from annotations."""
    try:
        accession_map = annotation.model_dump()["accession_map"]
    except KeyError as exc:
        raise ValueError(
            "The annotation is missing the required 'accession_map' field. "
            "Expected structure: {'accession_map': {<class_name>: {<old_id>: <new_id>, ...}, ...}}"
        ) from exc

    resource_accessions = accession_map.get(class_name)
    if resource_accessions is None:
        raise ValueError(f"No accession map found for class '{class_name}'.")

    return resource_accessions


def _update_resources(
    *,
    original_resources: FrozenDict[ResourceId, Resource],
    resource_accessions: AccessionMap,
    class_name: str,
) -> dict[ResourceId, Resource]:
    """Update resources with new resource ids."""
    updated_resources = {
        new_id: original_resources[old_id]
        for old_id, new_id in resource_accessions.items()
        if old_id in original_resources
    }

    missing_ids = set(original_resources) - set(resource_accessions)
    if missing_ids:
        raise ValueError(
            f"The following original resource IDs from class '{class_name}' are missing in the annotation's accession map: {missing_ids}."
        )
    return updated_resources


def _replace_ids_in_relations(
    *,
    modified_data: MutableDatapack,
    original_data: DataPack,
    target_class: str,
    resource_accessions: AccessionMap,
) -> None:
    """Replace resource IDs in relations of the modified data.

    Args:
        modified_data (dict): Dictionary representation of the modified data.
        original_data (DataPack): Original data.
        target_class (str): Class name whose resource ids are updated.
    """
    for class_name, class_resources in original_data.resources.items():
        for resource_id, resource in class_resources.items():
            relations = resource.relations
            if not relations:
                continue

            for relation_name, relation_spec in resource.relations.items():
                new_target_ids: str | set
                if relation_spec.targetClass != target_class:
                    continue

                target_resources = relation_spec.targetResources
                if not target_resources:
                    continue

                if isinstance(target_resources, str):
                    new_target_ids = resource_accessions[target_resources]
                elif isinstance(target_resources, frozenset):
                    new_target_ids = {
                        resource_accessions.get(target_resource)
                        for target_resource in target_resources
                    }
                else:
                    continue

                modified_data["resources"][class_name][resource_id]["relations"][
                    relation_name
                ] = {
                    "targetClass": target_class,
                    "targetResources": new_target_ids,
                }
