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

"""Data transformation logic for the 'replace resource ids' transformation"""

from collections.abc import Mapping

from arcticfreeze import FrozenDict
from pydantic import BaseModel, TypeAdapter

# ResourceRelation is not re-exported via schemapack.spec.datapack
from schemapack._internals.spec.datapack import ResourceRelation
from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.common.custom_types import (
    AccessionMap,
    ResourceId,
)
from metldata.builtin_transformations.common.validation import (
    validate_non_empty_annotation_ids,
)
from metldata.transform.exceptions import (
    EvitableTransformationError,
    InvalidAnnotationError,
)

# validates that the accession map's old and new ids are non-empty strings
_ACCESSION_MAP_ADAPTER = TypeAdapter(AccessionMap)


def replace_data_resource_ids(
    *,
    data: DataPack,
    class_name: str,
    annotation: BaseModel,
) -> DataPack:
    """Replace resource ids of a data class using annotations."""
    resource_accessions = _get_resource_accessions(
        annotation=annotation, class_name=class_name
    )

    original_resources = data.resources.get(class_name)
    if original_resources is None:
        raise EvitableTransformationError()

    # validate up front so a missing mapping is reported
    _assert_accession_map_is_complete(
        original_resources=original_resources,
        resource_accessions=resource_accessions,
        class_name=class_name,
    )

    all_resources = dict(data.resources)

    # rewrite relations that reference the renamed class, in all classes
    rebuilt_classes = _replace_ids_in_relations(
        original_data=data,
        resource_accessions=resource_accessions,
        target_class_name=class_name,
    )
    all_resources.update(rebuilt_classes)

    # re-key the renamed class itself
    all_resources[class_name] = _update_resources(
        original_resources=all_resources[class_name],
        resource_accessions=resource_accessions,
    )

    datapack_update: dict[str, object] = {"resources": FrozenDict(all_resources)}
    # if the datapack is rooted on the renamed class, the root resource is re-keyed
    if data.rootClass == class_name and data.rootResource is not None:
        datapack_update["rootResource"] = resource_accessions[data.rootResource]

    return data.model_copy(update=datapack_update)


def _get_resource_accessions(*, class_name: str, annotation: BaseModel) -> AccessionMap:
    """Extract resource ids from annotations."""
    accession_map = getattr(annotation, "accession_map", None)
    if accession_map is None:
        raise InvalidAnnotationError(
            "The annotation is missing the required 'accession_map' field. "
            "Expected structure: {'accession_map': {<class_name>: {<old_id>: <new_id>, ...}, ...}}"
        )

    resource_accessions = accession_map.get(class_name)
    if resource_accessions is None:
        raise InvalidAnnotationError(
            f"No accession map found for class '{class_name}'. "
            "Expected structure: {'accession_map': {<class_name>: {<old_id>: <new_id>, ...}, ...}}"
        )

    return validate_non_empty_annotation_ids(
        _ACCESSION_MAP_ADAPTER,
        resource_accessions,
        class_name=class_name,
        field_name="accession_map",
    )


def _assert_accession_map_is_complete(
    *,
    original_resources: Mapping[ResourceId, Resource],
    resource_accessions: AccessionMap,
    class_name: str,
) -> None:
    """Ensure every resource of the renamed class has a new id in the accession map.

    Raises:
        ValueError: if any resource of the class is missing from the accession map.
    """
    missing_ids = set(original_resources) - set(resource_accessions)
    if missing_ids:
        raise ValueError(
            f"The following original resource IDs from class '{class_name}' are missing"
            f" in the annotation's accession map: {missing_ids}."
        )


def _update_resources(
    *,
    original_resources: Mapping[ResourceId, Resource],
    resource_accessions: AccessionMap,
) -> FrozenDict[ResourceId, Resource]:
    """Re-key the resources of the renamed class with their new resource ids.

    The resources themselves are shared by reference; only the mapping keys
    change.
    """
    return FrozenDict(
        {
            new_id: original_resources[old_id]
            for old_id, new_id in resource_accessions.items()
            if old_id in original_resources
        }
    )


def _replace_ids_in_relations(
    *,
    original_data: DataPack,
    resource_accessions: AccessionMap,
    target_class_name: str,
) -> dict[str, FrozenDict[ResourceId, Resource]]:
    """Rebuild the resources whose relations reference the renamed class,
    replacing the old target resource ids with the new ones.

    Returns:
        A mapping from class name to the new resource map of that class, for
        every class in which at least one resource referenced
        ``target_class_name``. Classes without such references are omitted, so
        the caller keeps their existing resource maps (shared by reference).
    """
    rebuilt_classes: dict[str, FrozenDict[ResourceId, Resource]] = {}

    for class_name, class_resources in original_data.resources.items():
        changed_resources: dict[ResourceId, Resource] = {}
        for resource_id, resource in class_resources.items():
            updated_relations: dict[str, ResourceRelation] = {}
            for relation_name, relation in resource.relations.items():
                if relation.targetClass != target_class_name:
                    continue

                target_resources = relation.targetResources
                if not target_resources:
                    continue

                new_target_ids: frozenset[ResourceId] | ResourceId
                if isinstance(target_resources, str):
                    new_target_ids = resource_accessions[target_resources]
                else:
                    new_target_ids = frozenset(
                        resource_accessions[target_resource]
                        for target_resource in target_resources
                    )
                updated_relations[relation_name] = ResourceRelation(
                    targetClass=target_class_name,
                    targetResources=new_target_ids,
                )

            if updated_relations:
                changed_resources[resource_id] = resource.model_copy(
                    update={
                        "relations": FrozenDict(
                            {**resource.relations, **updated_relations}
                        )
                    }
                )

        if changed_resources:
            rebuilt_classes[class_name] = FrozenDict(
                {**class_resources, **changed_resources}
            )

    return rebuilt_classes
