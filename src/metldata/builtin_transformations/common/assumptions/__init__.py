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

from metldata.builtin_transformations.common.assumptions.path_assumptions import (
    assert_no_relation_target_multiplicity,  # noqa: F401
    assert_path_classes_and_relations_exist,  # noqa: F401
    assert_relation_target_multiplicity,  # noqa: F401
)
from metldata.builtin_transformations.common.assumptions.source_assumptions import (
    assert_class_is_source,  # noqa: F401
    assert_source_content_path_exists,  # noqa: F401
)
from metldata.builtin_transformations.common.assumptions.target_assumptions import (
    assert_object_path_exists,  # noqa: F401
)
