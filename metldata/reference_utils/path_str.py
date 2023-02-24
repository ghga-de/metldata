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

"""Data models"""

import re
from typing import Optional

NAME_PATTERN = r"[A-Za-z_]+\w*"
ACTIVE_ARROW_PATTERN = rf"\({NAME_PATTERN}\)>"
PASSIVE_ARROW_PATTERN = rf"<\({NAME_PATTERN}\)"
ARROW_PATTERN = rf"(({ACTIVE_ARROW_PATTERN})|({PASSIVE_ARROW_PATTERN}))"
ELEMENT_PATTERN = rf"{NAME_PATTERN}{ARROW_PATTERN}{NAME_PATTERN}"
PATH_RAW_CHAR_PATTERN = r"^[\w \n_><\(\)]+$"
PATH_PATTERN = (
    rf"^{NAME_PATTERN}{ARROW_PATTERN}({NAME_PATTERN}{ARROW_PATTERN})*{NAME_PATTERN}$"
)


class ValidationError(RuntimeError):
    """Raised when a path string was invalid"""


def validate_path_str_characters(path_str: str) -> None:
    """Validates the characters of the an uncleaned path str.

    Raises:
        ValidationError: if invalid.
    """

    if not re.match(PATH_RAW_CHAR_PATTERN, path_str):
        raise ValidationError(
            f"The following path string contains invalid characters: {path_str}"
        )


def validate_path_str_format(path_str: str) -> None:
    """Validates the format of the path str.

    Raises:
        ValidationError: if invalid.
    """

    if not re.match(PATH_PATTERN, path_str):
        raise ValidationError(
            f"The following path string has an invalid format: {path_str}"
        )


def clean_path_str(path_str: str) -> str:
    """Cleanup whitespaces and newlines."""

    return path_str.replace(" ", "").replace("\n", "")


def extract_first_element(*, path_str: str) -> str:
    """Extract the first element of a path_str.

    Raises:
        ValidationError: if no element can be extracted.
    """

    match = re.match(rf"^({ELEMENT_PATTERN}).*$", path_str)

    if not match:
        raise ValidationError(f"Cannot find element in path string: {path_str}")

    return match.group(1)


def get_target_class(*, path_str: str) -> str:
    """Get the target class of a path str."""

    match = re.match(rf"^.*?({NAME_PATTERN})$", path_str)

    if not match:
        raise ValidationError(f"Cannot find target class of path string: {path_str}")

    return match.group(1)


def split_first_element(*, path_str: str) -> tuple[str, Optional[str]]:
    """Return a tuple of the first element and the remaining path string.
    Thereby, the target class of the first element is set as the source class of the
    remaining path.
    The second field is none if the provided path only contained one element.
    """

    first_element = extract_first_element(path_str=path_str)
    first_element_target_class = get_target_class(path_str=first_element)

    if first_element == path_str:
        return first_element, None

    remaining_path = path_str[len(first_element) :]
    remaining_path_extended = first_element_target_class + remaining_path

    return first_element, remaining_path_extended


def get_string_elements(*, path_str: str) -> list[str]:
    """Decomposes a path string into elements in string repesentation."""

    elements: list[str] = []
    remaining_path = path_str

    # extract one element at a time:
    while True:
        element, remaining_path = split_first_element(path_str=remaining_path)
        elements.append(element)

        if not remaining_path:
            break

    return elements
