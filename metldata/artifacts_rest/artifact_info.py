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

"""Logic for handling information required for querying artifacts."""

import json
from typing import Optional

from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml_runtime.linkml_model.annotations import Annotation
from linkml_runtime.linkml_model.meta import ClassDefinition, ClassDefinitionName
from pydantic import BaseModel, Field, validator

from metldata.custom_types import Json
from metldata.model_utils.anchors import (
    AnchorPoint,
    get_anchors_points_by_target,
    lookup_anchor_point,
)
from metldata.model_utils.assumptions import check_basic_model_assumption
from metldata.model_utils.essentials import MetadataModel


class QueriableMetadataClass(BaseModel):
    """Model to describe a metadata class of an artifact that can be queried."""

    name: str = Field(..., description="The name of the metadata class.")
    description: Optional[str] = Field(
        None, description="A description of the metadata class."
    )
    anchor_point: AnchorPoint = Field(
        ..., description="The anchor point for this metadata class."
    )
    json_schema: Json = Field(
        ..., description="The JSON schema for this metadata class."
    )


class ArtifactQueryInfo(BaseModel):
    """Model to describe general information on an artifact.
    Please note, it does not contain actual artifact instances derived from specific
    metadata.
    """

    name: str = Field(..., description="The name of the artifact.")
    description: str = Field(..., description="A description of the artifact.")

    queriable_classes: dict[str, QueriableMetadataClass] = Field(
        ...,
        description=(
            "A dictionary of metadata classes that can be queried for this artifact."
            + " The keys are the name of the metadata classes. The values are the"
            + " corresponding metadata class models."
        ),
    )

    # pylint: disable=no-self-argument
    @validator("queriable_classes")
    def check_queriable_class_names(
        cls, value: dict[str, QueriableMetadataClass]
    ) -> dict[str, QueriableMetadataClass]:
        """Check if the keys of the `queriable_classes` dictionary correspond to the
        names of the metadata classes.
        """

        for class_name, queriable_class in value.items():
            if class_name != queriable_class.name:
                raise ValueError(
                    f"Key '{class_name}' of 'queriable_classes' does not match"
                    + f" the name '{queriable_class.name}' of the corresponding"
                    + " metadata class."
                )

        return value


def is_class_hidden(*, class_definition: ClassDefinition) -> bool:
    """Check if a metadata class is annotated as `hidden`."""

    if not isinstance(class_definition.annotations, dict):
        raise RuntimeError(  # This should never happen
            f"Annotations of class {class_definition.name} are not a dictionary."
        )

    if "hidden" in class_definition.annotations:
        if not isinstance(class_definition.annotations["hidden"], Annotation):
            raise RuntimeError(  # This should never happen
                f"Annotation 'hidden' of class {class_definition.name} has an"
                + " unexpected format."
            )

        if not isinstance(class_definition.annotations["hidden"].value, bool):
            raise RuntimeError(  # This should never happen
                f"Annotation 'hidden' of class {class_definition.name} has an"
                + " unexpected value."
            )

        return class_definition.annotations["hidden"].value

    return False


def get_queriable_metadata_class_names(*, model: MetadataModel) -> list[str]:
    """Get the names of all metadata classes that can be queried from a metadata model.
    Metadata are annotated as `hidden` are excluded from the list.
    """

    anchored_class_names = get_anchors_points_by_target(model=model).keys()
    schema_view = model.schema_view

    return [
        anchored_class_name
        for anchored_class_name in anchored_class_names
        if not is_class_hidden(
            class_definition=schema_view.get_class(anchored_class_name, strict=True)
        )
    ]


def load_json_schema_for_class(*, model: MetadataModel, class_name: str) -> Json:
    """Load the JSON schema for the specified class of the metadata model."""

    return json.loads(
        JsonSchemaGenerator(
            model, top_class=ClassDefinitionName(class_name)
        ).serialize()
    )


def load_description_for_class(
    *, model: MetadataModel, class_name: str
) -> Optional[str]:
    """Load the description for the specified class of the metadata model."""

    return model.schema_view.get_class(class_name, strict=True).description


def load_queriable_metadata_classes(
    *, model: MetadataModel
) -> dict[str, QueriableMetadataClass]:
    """Load all metadata classes that can be queried from a metadata model.

    Args:
        model: The metadata model.

    Returns:
        A dictionary of metadata classes that can be queried for this artifact.
        The keys are the name of the metadata classes. The values are the
        corresponding metadata class models.
    """

    anchor_points_by_target = get_anchors_points_by_target(model=model)

    queriable_class_names = get_queriable_metadata_class_names(model=model)

    return {
        queriable_class_name: QueriableMetadataClass(
            name=queriable_class_name,
            description=load_description_for_class(
                model=model, class_name=queriable_class_name
            ),
            anchor_point=lookup_anchor_point(
                class_name=queriable_class_name,
                anchor_points_by_target=anchor_points_by_target,
            ),
            json_schema=load_json_schema_for_class(
                model=model, class_name=queriable_class_name
            ),
        )
        for queriable_class_name in queriable_class_names
    }


def load_artifact_query_info(
    *, name: str, description: str, model: MetadataModel
) -> ArtifactQueryInfo:
    """Load artifact query info from a metadata model.

    Args:
        name: The name of the artifact.
        description: A description of the artifact.
        model: The metadata model for the artifact.

    Returns:
        The artifact query info model.
    """

    check_basic_model_assumption(model)

    queriable_classes = load_queriable_metadata_classes(model=model)

    return ArtifactQueryInfo(
        name=name,
        description=description,
        queriable_classes=queriable_classes,
    )
