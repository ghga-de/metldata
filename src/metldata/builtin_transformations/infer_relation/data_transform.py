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
from schemapack.spec.schemapack import ClassDefinition, ClassRelation, SchemaPack

from metldata.builtin_transformations.common.custom_types import (
    MutableClassResources,
    MutableDatapack,
    ResourceId,
)
from metldata.builtin_transformations.common.utils import data_to_dict
from metldata.builtin_transformations.infer_relation.config import (
    InferRelationConfig,
)
from metldata.builtin_transformations.infer_relation.resolve_path import (
    resolve_path,
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
    *, data: DataPack, model: SchemaPack, transformation_config: InferRelationConfig
) -> DataPack:
    """Adds inferred relations to the data as given in the configuration."""
    modified_data = data_to_dict(data)

    # name of the class to which the relation will be added
    class_name = transformation_config.class_name

    # name of the relation to be added
    relation_name = transformation_config.relation_name

    path = transformation_config.relation_path
    referenced_class = path.target

    # the target prefix refers to resources that will be modified by the transformation
    target_resources = get_class_resources(data=modified_data, class_name=class_name)

    for resource_id, resource in target_resources.items():
        relation_target_ids = resolve_path(
            data=data, source_resource_id=resource_id, path=path
        )
        type_corrected_relation_target_ids = modify_relation_target_ids_type(
            model, class_name, relation_name, relation_target_ids
        )
        # add a new relation to that resource
        resource.setdefault("relations", {})[relation_name] = {
            "targetClass": referenced_class,
            "targetResources": type_corrected_relation_target_ids,
        }
    return DataPack.model_validate(modified_data)


def modify_relation_target_ids_type(
    model: SchemaPack,
    class_name: str,
    relation_name: str,
    relation_target_ids: frozenset[ResourceId],
) -> frozenset[ResourceId] | ResourceId | None:
    """Post transformation modification of the relation target IDs type based on
    relation specification of the transformed model.

    This function does not handle the case where `relation_target_ids` is expected
    to contain a single item, but `resolve_path` returns multiple values. Such cases
    will trigger a validation error in post-transformation validation.
    """
    class_definition = get_class_definition(model, class_name)

    relation_spec = get_relation_specification(class_definition, relation_name)

    # If relation expects single target and relation_target_ids has 0 or 1 item,
    # return single item or None
    expects_single_target = not relation_spec.multiple.target
    has_at_most_one_target = len(relation_target_ids) < 2
    if expects_single_target and has_at_most_one_target:
        return next(iter(relation_target_ids), None)

    return relation_target_ids


def get_class_definition(model: SchemaPack, class_name: str) -> ClassDefinition:
    """Get the class definition from the model by its name."""
    class_definition = model.classes.get(class_name)
    if class_definition is None:
        raise EvitableTransformationError()
    return class_definition


def get_relation_specification(
    class_def: ClassDefinition, relation_name: str
) -> ClassRelation:
    """Get the relation specification from the class definition by its name."""
    relation_multiplicity_specification = class_def.relations.get(relation_name)
    if relation_multiplicity_specification is None:
        raise EvitableTransformationError()
    return relation_multiplicity_specification
