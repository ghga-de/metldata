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

"""Logic for handling relation paths."""

from pydantic import GetJsonSchemaHandler, ValidationInfo

from metldata.schemapack_.builtin_transformations.infer_relations.path.path_str import (
    PATH_PATTERN,
    ValidationError,
    clean_path_str,
    path_str_to_object_elements,
)


class RelationPath:
    """A model describing the path of a relation between classes of a metadata model.

    The relation path has two available representation. A string-based ("path_str"
    attribute) and an element-based ("elements" attribute) one.

    In the string-based representation ("path_str" attribute), the first and the last
    word correspond to the name of the source and target class respectively. ">" and "<"
    means active (left class refers the right one) and passive (the left
    class is referenced by the right one). Parentheses attached to these angles thereby
    indicate the property name of the referencing class. E.g. "class_a(class_b)>class_b"
    means that the source class "class_a" has a property "class_b" that relations the
    target class "class_b". Or "class_a<(class_a)class_b" means that the source
    class "class_a" is relation by the target class "class_b" via its properties
    "class_a". Reference paths can also involve additional classes. E.g. a string of
    "class_a<(class_a)class_b(class_c)>class_c" means that
    a relation from the source class "class_a" to the target class "class_c" can be
    established via an additional class "class_b". Any inserted spaces or newlines will
    be ignored. So the following paths are equivalent:
        - "class_a (class_b)> class_b"
        - "class_a
            (class_b)>
            class_b"

    A relation path consists of one or more elements. An element is a relationship
    between two classes. Reference paths that establish a direct relationship between
    source and target classes without the use of additional classes have only one
    element (e.g. in string representations "class_a(class_b)>class_b" or
    "class_a<(class_a)class_b"). More complex paths consist of multiple elements.
    E.g. the path "class_a<(class_a)class_b(class_c)>class_c" can be decomposed
    into the elements: "class_a<(class_a)class_b" and
    "class_b(class_c)>class_c".

    The elements of a ReferencePath are stored in the "elements" attribute as a list
    of ReferencePathElement objects that are optimized for programmatic use.

    The "source" attribute provides the source class of the path while the
    "target" attribute provides the target class of the path.
    """

    def __init__(self, *, path_str: str):
        """Construct relation path from a string-based representation."""
        self.path_str = clean_path_str(path_str=path_str)
        self.elements = path_str_to_object_elements(path_str=self.path_str)
        self.source = self.elements[0].source
        self.target = self.elements[-1].target

    @classmethod
    def validate(cls, value, info: ValidationInfo) -> "RelationPath":
        """A validator for pydantic."""
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise ValueError("A string is required.")

        try:
            return cls(path_str=value)
        except ValidationError as error:
            raise ValueError(str(error)) from ValidationError

    @classmethod
    def __get_validators__(cls):
        """To get validators for pydantic"""
        yield cls.validate

    @classmethod
    def __get_pydantic_json_schema__(
        cls, field_schema: dict, handler: GetJsonSchemaHandler
    ):
        """Modify the field schema for pydantic."""
        field_schema.update(type="string", pattern=PATH_PATTERN)

    def __hash__(self):
        """Calculate a hash."""
        return hash(self.path_str)

    def __eq__(self, other: object):
        """For comparisons."""
        if not isinstance(other, RelationPath):
            return NotImplemented

        return self.path_str == other.path_str

    def __repr__(self):
        """For representation."""
        return f"RelationPath(path_str='{self.path_str}')"

    def __str__(self):
        """For string representation."""
        return self.path_str
