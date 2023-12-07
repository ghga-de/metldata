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

"""Modelling inferred relations."""

from pydantic import BaseModel, ConfigDict, Field, model_validator
from schemapack.spec.schemapack import Cardinality

from metldata.schemapack_.builtin_transformations.infer_relations.path.path import (
    RelationPath,
)


class RelationDetails(BaseModel):
    """A base model for describing an inferred relation that is based on existing
    relations.
    """

    path: RelationPath = Field(
        ...,
        description=(
            "The path to reconstruct the new relation based on existing relations."
        ),
    )
    expect_multiple: bool = Field(
        True,
        description=(
            "Whether multiple target resources to expect for this relation."
            + " `True` corresponds to a `many_to_many` cardinality, `False` represents"
            + " a `many_to_one` cardinality. `one_to_one` or `one_to_many`"
            + "  cardinalities are currently not possible for inferred relations."
        ),
    )


class InferredRelations(RelationDetails):
    """A model for describing an inferred relation that is based on existing
    relations.
    """

    model_config = ConfigDict(frozen=True)

    source: str = Field(
        ..., description="The source class to which this relation should be added."
    )
    target: str = Field(..., description="The class targeted by this relation.")
    new_property: str = Field(
        ...,
        description=(
            "The name of the new property in the source to store the inferred relation."
        ),
    )

    @model_validator(mode="after")
    @classmethod
    def validate_source_and_target(cls, values):
        """Validate that the source and target attributes are identical with the
        source and target specified in the path.
        """
        if values.source != values.path.source:
            raise ValueError(
                "The source is not identical with the source of the specified path."
            )

        if values.target != values.path.target:
            raise ValueError(
                "The target is not identical with the target of the specified path."
            )

        return values
