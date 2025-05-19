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

"Assumptions for delete reference transformation"

from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.assumptions.path_assumptions import (
    check_class_exists,
)
from metldata.builtin_transformations.delete_class.config import (
    DeleteClassConfig,
)


def check_model_assumptions(
    schema: SchemaPack,
    transformation_config: DeleteClassConfig,
) -> None:
    """Check model assumptions for the delete reference transformation."""
    check_class_exists(model=schema, class_name=transformation_config.class_name)
