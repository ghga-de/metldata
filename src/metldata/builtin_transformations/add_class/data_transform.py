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

"""Data transformation logic for the 'add class' transformation."""

import jsonschema
from pydantic import BaseModel
from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.add_class.config import RelationSpec
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.transform.exceptions import (
    DataTransformationError,
    EvitableTransformationError,
    InvalidAnnotationError,
)


def add_data_class(
    *,
    data: DataPack,
    annotation: BaseModel,
    class_name: str,
    content_schema: dict,
    relations: list[RelationSpec],
) -> DataPack:
    """Add a new class entry to the provided data."""
    modified_data = data_to_dict(data)

    try:
        annotation_resources = annotation.model_dump()["resources"][class_name]
    except (KeyError, TypeError) as exc:
        raise InvalidAnnotationError(
            "The annotation is missing the required 'resources' field. "
            "Expected structure: {'resources': {<class_name>: {<resource_id>: {'content': {...}, 'relations': {...}}, ...}, ...}}"
        ) from exc

    if class_name in modified_data["resources"]:
        raise EvitableTransformationError()

    modified_data["resources"][class_name] = {
        resource_id: {
            "content": _get_resource_content(
                resource=resource, content_schema=content_schema
            ),
            "relations": _get_resource_relations(
                data=data, resource=resource, relations=relations
            ),
        }
        for resource_id, resource in annotation_resources.items()
    }

    return DataPack.model_validate(modified_data)


def _get_resource_content(*, resource: dict, content_schema: dict) -> dict:
    """Extract the content of a resource according to the content schema."""
    content_properties = set(content_schema.get("properties", {}).keys())
    content = {
        key: value for key, value in resource.items() if key in content_properties
    }
    try:
        jsonschema.validate(content, content_schema)
    except jsonschema.ValidationError as exc:
        raise DataTransformationError(
            f"Resource content does not match the content schema: {exc.message}"
        ) from exc

    return content


def _get_resource_relations(
    *, data: DataPack, resource: dict, relations: list[RelationSpec]
) -> dict:
    """Map each relation spec to the resource's resolved relation entry."""
    return {
        relation.relation_property_name: _resolve_relation(
            data=data, resource=resource, relation=relation
        )
        for relation in relations
    }


def _resolve_relation(
    *, data: DataPack, resource: dict, relation: RelationSpec
) -> dict:
    """Resolve a single relation entry for one annotated resource."""
    matched_ids = _matched_target_ids(data=data, resource=resource, relation=relation)
    return {
        "targetClass": relation.targetClass,
        "targetResources": _apply_target_cardinality(
            matched_ids=matched_ids, relation=relation
        ),
    }


def _matched_target_ids(
    *, data: DataPack, resource: dict, relation: RelationSpec
) -> list[str]:
    """Return the referenced IDs that exist in the relation's ``targetClass``.

    An annotation field whose IDs span several classes is partitioned by keeping, per
    relation spec, only the IDs present in that spec's ``targetClass``.
    """
    referenced_ids = resource.get(relation.target_resources) or []
    if isinstance(referenced_ids, str):
        referenced_ids = [referenced_ids]
    target_class_resources = data.resources[relation.targetClass].keys()
    return [id_ for id_ in referenced_ids if id_ in target_class_resources]


def _apply_target_cardinality(
    *, matched_ids: list[str], relation: RelationSpec
) -> list[str] | str | None:
    """Shape matched target IDs to the relation's target cardinality."""
    if relation.multiple.target:
        return matched_ids
    if len(matched_ids) > 1:
        raise DataTransformationError(
            f"Expected at most one target resource for relation "
            f"'{relation.relation_property_name}', but found multiple: {matched_ids}"
        )
    return matched_ids[0] if matched_ids else None
