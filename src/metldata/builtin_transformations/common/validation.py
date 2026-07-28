# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Helpers to validate annotation-supplied ids at transformation boundaries."""

from pydantic import TypeAdapter, ValidationError

from metldata.transform.exceptions import InvalidAnnotationError


def validate_non_empty_annotation_ids[T](
    adapter: TypeAdapter[T], value: object, *, class_name: str, field_name: str
) -> T:
    """Validate that an annotation field's resource ids are non-empty strings.

    Raises:
        InvalidAnnotationError: if validation fails.
    """
    try:
        return adapter.validate_python(value)
    except ValidationError as error:
        raise InvalidAnnotationError(
            f"The '{field_name}' annotation for class '{class_name}' contains"
            f" invalid ids: {error}"
        ) from error
