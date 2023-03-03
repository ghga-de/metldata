,bi1p# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Models used to describe inferred references based on existing references."""

from typing import Mapping

from pydantic import BaseModel

from metldata.reference.path import ReferencePath


class InferredReference:
    """"""

    path: ReferencePath
    multivalued: bool

    @property
    def source(self) -> str:
        """The name of the source class."""

        return self.path.source

    @property
    def target(self) -> str:
        """The name of the target class."""

        return self.path.target




class InferredRefMapElement:
    """"""

class InferredRefMap:
    """
    A model used describe inferred references based on existing references.

    It is a Mapping whereby the keys corresponds to the class name to which references
    should be added. The values are Mapp
    """

    @classmethod
    def validate(cls, value) -> "ReferencePath":
        """A validator for pydantic."""

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
    def __modify_schema__(cls, field_schema: dict):
        """Modify the field schema for pydantic."""

        field_schema.update(type="string", pattern=PATH_PATTERN)

    def __eq__(self, other: object):
        """For comparisons."""

        if not isinstance(other, ReferencePath):
            return NotImplemented

        return self.path_str == other.path_str
