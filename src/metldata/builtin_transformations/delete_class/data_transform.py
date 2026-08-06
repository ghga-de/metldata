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

"""Data transformation logic for the 'delete class' transformation"""

from arcticfreeze import FrozenDict
from schemapack.spec.datapack import DataPack, Resource

from metldata.builtin_transformations.common.custom_types import ResourceId
from metldata.transform.exceptions import EvitableTransformationError


def delete_data_class(*, data: DataPack, class_name: str) -> DataPack:
    """Delete class from the provided data."""
    all_resources = dict(data.resources)

    try:
        # drop the deleted class
        del all_resources[class_name]
    except KeyError as exc:
        raise EvitableTransformationError() from exc

    # replace the class maps in which resources referenced the deleted class;
    # classes without such references keep their existing maps
    rebuilt_classes = _remove_relations_from_data(
        original_data=data, target_class=class_name
    )
    all_resources.update(rebuilt_classes)

    return data.model_copy(update={"resources": FrozenDict(all_resources)})


def _remove_relations_from_data(
    *, original_data: DataPack, target_class: str
) -> dict[str, FrozenDict[ResourceId, Resource]]:
    """Rebuild the resources whose relations reference the deleted class.

    Args:
        original_data (DataPack): Original data
        target_class (str): Name of the class to be deleted

    Returns:
        A mapping from class name to the new resource map of that class, for
        every class in which at least one resource referenced ``target_class``.
        Classes without such references are omitted, so the caller keeps their
        existing resource maps (shared by reference).
    """
    rebuilt_classes: dict[str, FrozenDict[ResourceId, Resource]] = {}

    for class_name, class_resources in original_data.resources.items():
        if class_name == target_class:
            continue

        changed_resources: dict[ResourceId, Resource] = {}
        for resource_id, resource in class_resources.items():
            remaining_relations = {
                name: relation
                for name, relation in resource.relations.items()
                if relation.targetClass != target_class
            }
            # a shorter dict means at least one relation referenced the deleted
            # class and was dropped, so this resource needs rebuilding
            if len(remaining_relations) != len(resource.relations):
                changed_resources[resource_id] = resource.model_copy(
                    update={"relations": FrozenDict(remaining_relations)}
                )

        if changed_resources:
            rebuilt_classes[class_name] = FrozenDict(
                {**class_resources, **changed_resources}
            )

    return rebuilt_classes
