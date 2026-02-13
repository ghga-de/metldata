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
#

"""Built-in transformations"""

from metldata.builtin_transformations.delete_class import (
    DELETE_CLASS_TRANSFORMATION,  # noqa: F401
)
from metldata.builtin_transformations.duplicate_class import (
    DUPLICATE_CLASS_TRANSFORMATION,  # noqa: F401
)
from metldata.builtin_transformations.infer_relation import (
    INFER_RELATION_TRANSFORMATION,  # noqa: F401
)
from metldata.builtin_transformations.merge_relations import (
    MERGE_RELATIONS_TRANSFORMATION,  # noqa: F401
)
from metldata.builtin_transformations.rename_id_property import (
    RENAME_ID_PROPERTY_TRANSFORMATION,  # noqa: F401
)
from metldata.builtin_transformations.replace_resource_ids import (
    REPLACE_RESOURCE_IDS_TRANSFORMATION,  # noqa: F401
)
from metldata.builtin_transformations.transform_content import (
    TRANSFORM_CONTENT_TRANSFORMATION,  # noqa: F401
)
