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
#

"""Models used to describe all inferred relations based on existing relations."""

from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from metldata.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
    RelationDetails,
)


class RelationInferenceConfig(BaseSettings):
    """Config containing instructions to infer relations for all classes of a model."""

    model_config = SettingsConfigDict(extra="forbid")

    inferred_relations: dict[str, dict[str, RelationDetails]] = Field(
        ...,
        description=(
            "A nested dictionary describing instructions to infer relations based"
            + " on existing relations. On the first level keys refer to classes to"
            + " which the inferred relations should be added. On the second level, keys"
            + " refer to the names of the new property of the host class that hold the"
            + " inferred relation. The values refer to the actual relation details."
        ),
        examples=[
            {
                "ClassA": {
                    "class_d": {
                        "path": "ClassA(class_b)>ClassB(class_d)>ClassD",
                        "cardinality": "many_to_many",
                    },
                    "class_c": {
                        "path": "ClassA(class_b)>ClassB<(class_c)ClassC",
                        "cardinality": "many_to_one",
                    },
                },
                "ClassB": {
                    "class_c": {
                        "path": "ClassB<(class_c)ClassC",
                        "cardinality": "many_to_many",
                    }
                },
            }
        ],
    )

    @cached_property
    def inference_instructions(self) -> list[InferenceInstruction]:
        """A list of inferred relations."""
        return [
            InferenceInstruction(
                source=source,
                target=relation_details.path.target,
                path=relation_details.path,
                new_property=property_name,
                allow_multiple=relation_details.allow_multiple,
            )
            for source, slot_description in self.inferred_relations.items()
            for property_name, relation_details in slot_description.items()
        ]
