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

"""Test reference utils."""

from contextlib import nullcontext
from typing import Optional

import pytest

from metldata.reference_utils.path_str import (
    ValidationError,
    validate_path_str_characters,
    validate_path_str_format,
    extract_first_element,
    get_target_class,
    split_first_element,
    get_string_elements,
)


@pytest.mark.parametrize(
    "path_str, is_valid",
    [
        ("class_a(has_class_b)>class_b", True),
        ("class_a<(has_class_a)class_b", True),
        ("class_a(has_class_b) >class_b", True),
        ("class_a(has_cl ass_b)>class_b", True),
        ("class_a(has_class_b)>\nclass_b", True),
        ("class_1(has_class_2)>class_2", True),
        ("ClassA(has_class_b)>ClassB", True),
        ("class-a(has-class_b)>class-b", False),
        ("class_a.has_class_b>class_b", False),
    ],
)
def test_validate_path_str_characters(path_str: str, is_valid: bool):
    """Test the validate_path_str_characters method."""

    with nullcontext() if is_valid else pytest.raises(ValidationError):
        validate_path_str_characters(path_str)


@pytest.mark.parametrize(
    "path_str, is_valid",
    [
        ("class_a(has_class_b)>class_b", True),
        ("class_a<(has_class_a)class_b", True),
        ("class_a(has_class_b)>class_b(has_class_c)>class_c", True),
        ("class_a<(has_class_a)class_b(has_class_c)>class_c", True),
        ("class_a<(has_class_a)class_b<(has_class_b)class_c", True),
        (
            "class_a(has_class_b)>class_b(has_class_c)>class_c(has_class_d)>class_d",
            True,
        ),
        ("class_a<(has_class_b)>class_b", False),
        ("class_a>class_b", False),
        ("class_a>(has_class_a)class_b", False),
        ("class_a(has_class_b)<class_b", False),
        ("class_a(has_class_b)>class_b(has_class_c)>", False),
        ("(has_class_b)>class_b(has_class_c)>class_c", False),
        ("class_a(has_class_b>class_b", False),
    ],
)
def test_validate_path_str_format(path_str: str, is_valid: bool):
    """Test the validate_path_str_format method."""

    with nullcontext() if is_valid else pytest.raises(ValidationError):
        validate_path_str_format(path_str)


@pytest.mark.parametrize(
    "path_str, expected_first_element",
    [
        ("class_a(has_class_b)>class_b", "class_a(has_class_b)>class_b"),
        ("class_a<(has_class_a)class_b", "class_a<(has_class_a)class_b"),
        (
            "class_a(has_class_b)>class_b(has_class_c)>class_c",
            "class_a(has_class_b)>class_b",
        ),
    ],
)
def test_extract_first_element(path_str: str, expected_first_element: str):
    """Test the extract_first_element method."""

    observed_first_element = extract_first_element(path_str=path_str)
    assert observed_first_element == expected_first_element


@pytest.mark.parametrize(
    "path_str, expected_target_class",
    [
        ("class_a(has_class_b)>class_b", "class_b"),
        ("class_a<(has_class_a)class_b", "class_b"),
        (
            "class_a(has_class_b)>class_b(has_class_c)>class_c",
            "class_c",
        ),
    ],
)
def test_get_target_class(path_str: str, expected_target_class: str):
    """Test the get_target_class method."""

    observed_target_class = get_target_class(path_str=path_str)
    assert observed_target_class == expected_target_class


@pytest.mark.parametrize(
    "path_str, expected_first_element, expected_remaining_path",
    [
        ("class_a(has_class_b)>class_b", "class_a(has_class_b)>class_b", None),
        ("class_a<(has_class_a)class_b", "class_a<(has_class_a)class_b", None),
        (
            "class_a(has_class_b)>class_b(has_class_c)>class_c",
            "class_a(has_class_b)>class_b",
            "class_b(has_class_c)>class_c",
        ),
    ],
)
def test_split_first_element(
    path_str: str, expected_first_element: str, expected_remaining_path: Optional[str]
):
    """Test the split_first_element method."""

    observed_first_element, observed_remaining_path = split_first_element(
        path_str=path_str
    )
    assert observed_first_element == expected_first_element
    assert observed_remaining_path == expected_remaining_path


@pytest.mark.parametrize(
    "path_str, expected_elements",
    [
        ("class_a(has_class_b)>class_b", ["class_a(has_class_b)>class_b"]),
        ("class_a<(has_class_a)class_b", ["class_a<(has_class_a)class_b"]),
        (
            "class_a(has_class_b)>class_b(has_class_c)>class_c",
            [
                "class_a(has_class_b)>class_b",
                "class_b(has_class_c)>class_c",
            ],
        ),
    ],
)
def test_get_string_elements(path_str: str, expected_elements: list[str]):
    """Test the get_string_elements method."""

    observed_elements = get_string_elements(path_str=path_str)
    assert observed_elements == expected_elements
