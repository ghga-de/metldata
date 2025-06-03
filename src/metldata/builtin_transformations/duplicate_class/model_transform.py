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

"""Model transformation logic for the 'duplicate class' transformation"""

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.utils import model_to_dict
from metldata.builtin_transformations.duplicate_class.config import (
    DuplicateClassConfig,
)
from metldata.transform.exceptions import EvitableTransformationError


def duplicate_model_class(
    *,
    model: SchemaPack,
    transformation_config: DuplicateClassConfig,
) -> SchemaPack:
    """Duplicate a source class definition in the model under a given target class name."""
    mutable_model = model_to_dict(model)

    source_class_name = transformation_config.source_class_name
    target_class_name = transformation_config.target_class_name
    try:
        source_class_definition = mutable_model["classes"][source_class_name]
        mutable_model["classes"][target_class_name] = source_class_definition
    except KeyError as exc:
        raise EvitableTransformationError() from exc

    return SchemaPack.model_validate(mutable_model)
