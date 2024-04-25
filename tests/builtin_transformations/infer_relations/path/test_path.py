# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Test the path module."""

from contextlib import nullcontext

import pytest
from pydantic import BaseModel

from metldata.builtin_transformations.infer_relations.path.path import (
    RelationPath,
)
from metldata.builtin_transformations.infer_relations.path.path_elements import (
    RelationPathElement,
    RelationPathElementType,
)


@pytest.mark.parametrize(
    "path_str, expected_elements, expected_source, expected_target",
    [
        (
            "class_a(class_b)>class_b",
            [
                RelationPathElement(
                    type_=RelationPathElementType.ACTIVE,
                    source="class_a",
                    property="class_b",
                    target="class_b",
                )
            ],
            "class_a",
            "class_b",
        ),
        (
            """class_a
                (class_b) >
                class_b""",  # containing whitespaces
            [
                RelationPathElement(
                    type_=RelationPathElementType.ACTIVE,
                    source="class_a",
                    property="class_b",
                    target="class_b",
                )
            ],
            "class_a",
            "class_b",
        ),
        (
            "class_a<(class_a)class_b",
            [
                RelationPathElement(
                    type_=RelationPathElementType.PASSIVE,
                    source="class_a",
                    property="class_a",
                    target="class_b",
                )
            ],
            "class_a",
            "class_b",
        ),
        (
            "class_a(class_b)>class_b(class_c)>class_c",
            [
                RelationPathElement(
                    type_=RelationPathElementType.ACTIVE,
                    source="class_a",
                    property="class_b",
                    target="class_b",
                ),
                RelationPathElement(
                    type_=RelationPathElementType.ACTIVE,
                    source="class_b",
                    property="class_c",
                    target="class_c",
                ),
            ],
            "class_a",
            "class_c",
        ),
        (
            "class_a(class_b)>class_b<(class_b)class_c",
            [
                RelationPathElement(
                    type_=RelationPathElementType.ACTIVE,
                    source="class_a",
                    property="class_b",
                    target="class_b",
                ),
                RelationPathElement(
                    type_=RelationPathElementType.PASSIVE,
                    source="class_b",
                    property="class_b",
                    target="class_c",
                ),
            ],
            "class_a",
            "class_c",
        ),
    ],
)
def test_reference_path(
    path_str: str,
    expected_elements: RelationPathElement,
    expected_source: str,
    expected_target: str,
):
    """Test the RelationPath class."""

    observed_path = RelationPath(path_str=path_str)
    assert observed_path.elements == expected_elements
    assert observed_path.source == expected_source
    assert observed_path.target == expected_target


@pytest.mark.parametrize(
    "path_str, is_valid",
    [
        ("class_a(class_b)>class_b", True),
        ("class_a<(class_a)class_b", True),
        ("class_a(class_b)>class_b(class_c)>class_c", True),
        (12312, False),
        ("class_a<(class_b)>class_b", False),
        ("(class_b)>class_b(class_c)>class_c", False),
    ],
)
def test_reference_path_pydantic(path_str: str, is_valid: bool):
    """Test the RelationPath class when used with pydantic."""

    class ExampleModel(BaseModel):
        """Some example model."""

        path: RelationPath

    with nullcontext() if is_valid else pytest.raises(ValueError):
        observed_path = ExampleModel(path=path_str).path  # type: ignore

    if is_valid:
        expected_path = RelationPath(path_str=path_str)
        assert observed_path == expected_path
