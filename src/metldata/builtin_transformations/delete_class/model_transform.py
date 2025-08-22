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

"""Model transformation logic for the 'delete class' transformation"""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.utils import model_to_dict
from metldata.transform.exceptions import EvitableTransformationError


def delete_model_class(*, model: SchemaPack, class_name: str) -> SchemaPack:
    """Delete class from the model."""
    mutable_model = model_to_dict(model)

    try:
        del mutable_model["classes"][class_name]
    except KeyError as exc:
        raise EvitableTransformationError() from exc

    _remove_relations_from_model(
        mutable_model=mutable_model,
        original_model=model,
        target_class=class_name,
    )

    return SchemaPack.model_validate(mutable_model)


def _remove_relations_from_model(
    *,
    mutable_model: dict,
    original_model: SchemaPack,
    target_class: str,
) -> None:
    """Remove relations associated to deleted class from the model.

    Args:
        mutable_model (dict): Dictionary representation of the model
        original_model (SchemaPack): Original model
        target_class (str): Class name to be deleted
    """
    for class_name, class_def in original_model.classes.items():
        if class_name == target_class:
            continue

        filtered_relations = {
            rel_name: rel_spec
            for rel_name, rel_spec in class_def.relations.items()
            if rel_spec.targetClass != target_class
        }
        mutable_model["classes"][class_name]["relations"] = filtered_relations
