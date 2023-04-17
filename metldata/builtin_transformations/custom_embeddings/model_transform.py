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

"""Logic for transforming metadata models."""

from copy import deepcopy
from typing import Any, cast
from stringcase import snakecase


from linkml_runtime.linkml_model.meta import ClassDefinition, SlotDefinition

from metldata.builtin_transformations.custom_embeddings.embedding_profile import (
    EmbeddingProfile,
)
from metldata.model_utils.anchors import AnchorPoint, get_anchors_points_by_target
from metldata.model_utils.essentials import ExportableSchemaView, MetadataModel
from metldata.model_utils.manipulate import add_slot_usage_annotation, add_anchor_point
from metldata.model_utils.identifiers import get_class_identifier
from metldata.transform.base import MetadataModelTransformationError


def get_slot_in_context_of_class(
    *, schema_view: ExportableSchemaView, slot_name: str, class_name: str
):
    """Get the definition of slot in context of a class based on the slot_usage of that
    class. If the slot is not defined in slot usage, return an empty slot definition."""


def generated_embedded_class(
    *,
    schema_view: ExportableSchemaView,
    embedding_profile: EmbeddingProfile,
    anchor_points_by_target: dict[str, AnchorPoint],
) -> ClassDefinition:
    """Generate an embedded class from an embedding profile."""

    class_to_embed = schema_view.get_class(embedding_profile.source_class)
    if not class_to_embed:
        raise MetadataModelTransformationError(
            f"Could not find class {embedding_profile.source_class} in model"
        )

    embedded_class = deepcopy(class_to_embed)

    # rename the class:
    embedded_class.name = embedding_profile.embedded_class

    if not embedded_class.slots:
        embedded_class.slots = []

    if not embedded_class.slot_usage:
        embedded_class.slot_usage = {}

    if not isinstance(embedded_class.slot_usage, dict):
        raise RuntimeError(  # This should never happen
            f"slot_usage of class '{embedding_profile.source_class}' is not a dict"
        )
    embedded_class.slot_usage = cast(dict[str, Any], embedded_class.slot_usage)

    # mark slots that point to embedded references as inlined:
    for (
        target_slot_name,
        target_embedding_profile,
    ) in embedding_profile.embedded_references.items():
        # Extract the target slot definition from the slot_usage of the embedded class,
        # if it is not defined there, create a new empty slot definition and add it to
        # the slot_usage of the embedded class:
        target_slot_definition = embedded_class.slot_usage.get(target_slot_name)
        if not target_slot_definition:
            if not target_slot_name in embedded_class.slots:
                raise MetadataModelTransformationError(
                    f"Could not find slot {target_slot_name} in class {class_to_embed.name}"
                )
            if not schema_view.get_slot(slot_name=target_slot_name):
                raise MetadataModelTransformationError(
                    f"Could not find slot {target_slot_name} in model"
                )
            target_slot_definition = SlotDefinition(name=target_slot_name)
            embedded_class.slot_usage[target_slot_name] = target_slot_definition

        if not isinstance(target_slot_definition, SlotDefinition):
            raise RuntimeError(  # This should never happen
                f"The values of slot_usage of class '{embedding_profile.source_class}'"
                + f" are not of type SlotDefinition"
            )
        target_slot_definition = cast(SlotDefinition, target_slot_definition)

        # set the target slot to inlined:
        target_slot_definition.inlined = True
        target_slot_definition.inlined_as_list = True

    return embedded_class


def add_custom_embedded_class(
    *,
    model: MetadataModel,
    embedding_profile: EmbeddingProfile,
    anchor_points_by_target: dict[str, AnchorPoint],
) -> MetadataModel:
    """Add a custom embedded class to a metadata model."""

    embedded_class = generated_embedded_class(
        model=model,
        embedding_profile=embedding_profile,
        anchor_points_by_target=anchor_points_by_target,
    )

    schema_view = model.schema_view
    schema_view.add_class(embedded_class)

    # add anchor point for embedded class:
    identifier_slot = get_class_identifier(
        model=model, class_name=embedding_profile.source_class
    )
    if not identifier_slot:
        raise MetadataModelTransformationError(
            f"Could not find identifier slot for class {embedding_profile.source_class}"
        )
    anchor_point = AnchorPoint(
        root_slot=snakecase(embedding_profile.embedded_class),
        target_class=embedding_profile.embedded_class,
        identifier_slot=identifier_slot,
    )
    schema_view = add_anchor_point(schema_view=schema_view, anchor_point=anchor_point)

    return schema_view.export_model()


def mark_anchored_classes_as_hidden(
    *, model: MetadataModel, anchor_points_by_target: dict[str, AnchorPoint]
) -> MetadataModel:
    """Mark all classes that are anchored as hidden. Returns a copy of the model."""

    schema_view = model.schema_view

    for anchor_point in anchor_points_by_target.values():
        schema_view = add_slot_usage_annotation(
            schema_view=schema_view,
            slot_name=anchor_point.root_slot,
            class_name=anchor_point.target_class,
            annotation_key="hidden",
            annotation_value=True,
        )

    return schema_view.export_model()


def add_custom_embedded_classes(
    *, model: MetadataModel, embedding_profiles: list[EmbeddingProfile]
) -> MetadataModel:
    """Add custom embedded classes to a metadata model."""

    anchor_points_by_target = get_anchors_points_by_target(model=model)

    # mark all existing anchored classes as hidden, so that only the custom embedded
    # classes are visible:
    model = mark_anchored_classes_as_hidden(
        model=model, anchor_points_by_target=anchor_points_by_target
    )

    for embedding_profile in embedding_profiles:
        model = add_custom_embedded_class(
            model=model,
            embedding_profile=embedding_profile,
            anchor_points_by_target=anchor_points_by_target,
        )

    return model
