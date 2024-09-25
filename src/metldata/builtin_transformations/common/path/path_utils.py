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

"""Utility functions for Path operations"""

from metldata.builtin_transformations.common.path.path import RelationPath
from metldata.builtin_transformations.common.path.path_elements import (
    RelationPathElementType,
)
from metldata.transform.exceptions import (
    NotDirectRelationError,
)


def get_referred_class(relation_path: RelationPath) -> str:
    """Extracts and returns the class that is referred to in a direct relation path.

    Given a `RelationPath` object, this function identifies the target class that
    is referred to by another class within the path. The function handles both
    active and passive relationships and returns a str containing the name of the
    referred class (either the source or target class depending on the relation type).
    """
    elements = relation_path.elements
    if len(elements) != 1:
        raise NotDirectRelationError()

    path_element = elements[0]

    return (
        path_element.target
        if path_element.type_ == RelationPathElementType.ACTIVE
        else path_element.source
    )
