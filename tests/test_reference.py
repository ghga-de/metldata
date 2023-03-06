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
from pydantic import BaseModel

from metldata.reference.config import ReferenceMapConfig
from metldata.reference.path import ReferencePath
from metldata.reference.path_elements import (
    ReferencePathElement,
    ReferencePathElementType,
)
from metldata.reference.path_str import (
    ValidationError,
    extract_first_element,
    get_element_components,
    get_element_type,
    get_string_elements,
    get_target_class,
    path_str_to_object_elements,
    split_first_element,
    string_element_to_object,
    validate_path_str_characters,
    validate_path_str_format,
    validate_string_element,
)
from metldata.reference.reference import InferredReference


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

    with nullcontext() if is_valid else pytest.raises(ValidationError):  # type: ignore
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

    with nullcontext() if is_valid else pytest.raises(ValidationError):  # type: ignore
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


@pytest.mark.parametrize(
    "string_element, is_valid",
    [
        ("class_a(has_class_b)>class_b", True),
        ("class_a<(has_class_a)class_b", True),
        ("class_a<(has_class_a)>class_b", False),
        ("class_a>class_b", False),
        ("class_a(has_class_b)>class_b(has_class_c)>class_c", False),
    ],
)
def test_validate_string_element(string_element: str, is_valid: bool):
    """Test the validate_string_element method."""

    with nullcontext() if is_valid else pytest.raises(ValidationError):  # type: ignore
        validate_string_element(string_element)


@pytest.mark.parametrize(
    "string_element, expected_type",
    [
        ("class_a(has_class_b)>class_b", ReferencePathElementType.ACTIVE),
        ("class_a<(has_class_a)class_b", ReferencePathElementType.PASSIVE),
    ],
)
def test_get_element_type(string_element: str, expected_type: ReferencePathElementType):
    """Test the get_element_type method."""

    observed_type = get_element_type(string_element=string_element)
    assert observed_type == expected_type


@pytest.mark.parametrize(
    "string_element, expected_source, expected_slot, expected_target",
    [
        ("class_a(has_class_b)>class_b", "class_a", "has_class_b", "class_b"),
        ("class_a<(has_class_a)class_b", "class_a", "has_class_a", "class_b"),
    ],
)
def test_get_element_components(
    string_element: str, expected_source: str, expected_slot: str, expected_target: str
):
    """Test the get_element_components method."""

    observed_source, observed_slot, observed_target = get_element_components(
        string_element=string_element
    )
    assert observed_source == expected_source
    assert observed_slot == expected_slot
    assert observed_target == expected_target


@pytest.mark.parametrize(
    "string_element, expected_object",
    [
        (
            "class_a(has_class_b)>class_b",
            ReferencePathElement(
                type_=ReferencePathElementType.ACTIVE,
                source="class_a",
                slot="has_class_b",
                target="class_b",
            ),
        ),
        (
            "class_a<(has_class_a)class_b",
            ReferencePathElement(
                type_=ReferencePathElementType.PASSIVE,
                source="class_a",
                slot="has_class_a",
                target="class_b",
            ),
        ),
    ],
)
def test_string_element_to_object(
    string_element: str, expected_object: ReferencePathElement
):
    """Test the string_element_to_object method."""

    observed_object = string_element_to_object(string_element)
    assert observed_object == expected_object


@pytest.mark.parametrize(
    "path_str, expected_elements",
    [
        (
            "class_a(has_class_b)>class_b",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_a",
                    slot="has_class_b",
                    target="class_b",
                )
            ],
        ),
        (
            "class_a<(has_class_a)class_b",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.PASSIVE,
                    source="class_a",
                    slot="has_class_a",
                    target="class_b",
                )
            ],
        ),
        (
            "class_a(has_class_b)>class_b(has_class_c)>class_c",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_a",
                    slot="has_class_b",
                    target="class_b",
                ),
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_b",
                    slot="has_class_c",
                    target="class_c",
                ),
            ],
        ),
        (
            "class_a(has_class_b)>class_b<(has_class_b)class_c",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_a",
                    slot="has_class_b",
                    target="class_b",
                ),
                ReferencePathElement(
                    type_=ReferencePathElementType.PASSIVE,
                    source="class_b",
                    slot="has_class_b",
                    target="class_c",
                ),
            ],
        ),
    ],
)
def test_path_str_to_object_elements(
    path_str: str, expected_elements: ReferencePathElement
):
    """Test the path_str_to_object_elements method."""

    observed_elements = path_str_to_object_elements(path_str)
    assert observed_elements == expected_elements


@pytest.mark.parametrize(
    "path_str, expected_elements, expected_source, expected_target",
    [
        (
            "class_a(has_class_b)>class_b",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_a",
                    slot="has_class_b",
                    target="class_b",
                )
            ],
            "class_a",
            "class_b",
        ),
        (
            """class_a
                (has_class_b) >
                class_b""",  # containing whitespaces
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_a",
                    slot="has_class_b",
                    target="class_b",
                )
            ],
            "class_a",
            "class_b",
        ),
        (
            "class_a<(has_class_a)class_b",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.PASSIVE,
                    source="class_a",
                    slot="has_class_a",
                    target="class_b",
                )
            ],
            "class_a",
            "class_b",
        ),
        (
            "class_a(has_class_b)>class_b(has_class_c)>class_c",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_a",
                    slot="has_class_b",
                    target="class_b",
                ),
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_b",
                    slot="has_class_c",
                    target="class_c",
                ),
            ],
            "class_a",
            "class_c",
        ),
        (
            "class_a(has_class_b)>class_b<(has_class_b)class_c",
            [
                ReferencePathElement(
                    type_=ReferencePathElementType.ACTIVE,
                    source="class_a",
                    slot="has_class_b",
                    target="class_b",
                ),
                ReferencePathElement(
                    type_=ReferencePathElementType.PASSIVE,
                    source="class_b",
                    slot="has_class_b",
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
    expected_elements: ReferencePathElement,
    expected_source: str,
    expected_target: str,
):
    """Test the ReferencePath class."""

    observed_path = ReferencePath(path_str=path_str)
    assert observed_path.elements == expected_elements
    assert observed_path.source == expected_source
    assert observed_path.target == expected_target


@pytest.mark.parametrize(
    "path_str, is_valid",
    [
        ("class_a(has_class_b)>class_b", True),
        ("class_a<(has_class_a)class_b", True),
        ("class_a(has_class_b)>class_b(has_class_c)>class_c", True),
        (12312, False),
        ("class_a<(has_class_b)>class_b", False),
        ("(has_class_b)>class_b(has_class_c)>class_c", False),
    ],
)
def test_reference_path_pydantic(path_str: str, is_valid: bool):
    """Test the ReferencePath class when used with pydantic."""

    class ExampleModel(BaseModel):
        """Some example model."""

        path: ReferencePath

    with nullcontext() if is_valid else pytest.raises(ValueError):  # type: ignore
        observed_path = ExampleModel(path=path_str).path

    if is_valid:
        expected_path = ReferencePath(path_str=path_str)
        assert observed_path == expected_path


def test_reference_map_config():
    """Test the ReferenceMapConfig class."""

    inferred_ref_map = {
        "class_a": {
            "has_class_d": {
                "path": "class_a(has_class_b)>class_b(has_class_d)>class_d",
                "multivalued": False,
            },
            "has_class_c": {
                "path": "class_a(has_class_b)>class_b<(has_class_c)class_c",
                "multivalued": True,
            },
        },
        "class_b": {
            "has_class_c": {
                "path": "class_b<(has_class_c)class_c",
                "multivalued": True,
            }
        },
    }
    expected_refs = [
        InferredReference(
            source="class_a",
            target="class_d",
            path=ReferencePath(
                path_str="class_a(has_class_b)>class_b(has_class_d)>class_d"
            ),
            new_slot="has_class_d",
            multivalued=False,
        ),
        InferredReference(
            source="class_a",
            target="class_c",
            path=ReferencePath(
                path_str="class_a(has_class_b)>class_b<(has_class_c)class_c"
            ),
            new_slot="has_class_c",
            multivalued=True,
        ),
        InferredReference(
            source="class_b",
            target="class_c",
            path=ReferencePath(path_str="class_b<(has_class_c)class_c"),
            new_slot="has_class_c",
            multivalued=True,
        ),
    ]

    config = ReferenceMapConfig(inferred_ref_map=inferred_ref_map)
    observed_refs = config.inferred_references
    assert expected_refs == observed_refs