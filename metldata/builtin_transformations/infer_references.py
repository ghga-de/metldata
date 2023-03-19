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

"""A transformation to infer references based on existing ones in the metadata model."""

from linkml_runtime.linkml_model.meta import SlotDefinition

from metldata.model_utils.anchors import AnchorPoint, get_anchors_by_target
from metldata.model_utils.assumptions import check_basic_model_assumption
from metldata.model_utils.essentials import MetadataModel
from metldata.model_utils.manipulate import (
    ModelManipulationError,
    add_slot_if_not_exists,
    upsert_class_slot,
)
from metldata.reference.config import ReferenceMapConfig
from metldata.reference.path_elements import ReferencePathElement
from metldata.reference.reference import InferredReference
from metldata.transform.base import (
    Json,
    MetadataModelTransformationError,
    TransformationBase,
)


class PathElementResolutionError(RuntimeError):
    """Raised when a path element cannot be resolved."""


def inferred_reference_to_slot(reference: InferredReference) -> SlotDefinition:
    """Convert an inferred reference into a slot definition to be mounted on the
    source class."""

    return SlotDefinition(
        name=reference.new_slot,
        range=reference.target,
        multivalued=reference.multivalued,
    )


def add_reference_to_model(
    *, model: MetadataModel, reference: InferredReference
) -> MetadataModel:
    """Get a modified copy of the provided model with the inferred reference being
    added.

    Raises:
            MetadataModelTransformationError:
                if the transformation of the metadata model fails.
    """

    new_slot = inferred_reference_to_slot(reference)

    schema_view = model.schema_view
    try:
        schema_view = add_slot_if_not_exists(schema_view=schema_view, new_slot=new_slot)
        schema_view = upsert_class_slot(
            schema_view=schema_view, class_name=reference.source, new_slot=new_slot
        )
    except ModelManipulationError as error:
        raise MetadataModelTransformationError(
            f"Failed to add the inferred reference '{reference}' to the metadata"
            + " model.: {error}"
        ) from error

    return schema_view.export_model()


def resolve_path_element_target_ids(
    *, source_resource: Json, path_element: ReferencePathElement
) -> list[str]:
    """Resolve a reference path element applied to a metadata resource.

    Returns:
        A list of target IDs that are targeted by the path element in context of the
        provided source resource.

    Raises:
        PathElementResolutionError:
            if the path element cannot be resolved.
    """

    target_ids = source_resource.get(path_element.slot)

    if target_ids is None:
        raise PathElementResolutionError(
            f"Cannot resolve path element '{path_element}' because the slot"
            + f" '{path_element.slot}' is not present in the source resource"
            + f" '{source_resource}'."
        )

    # convert single value to list:
    if not isinstance(target_ids, list):
        target_ids = [target_ids]

    # check that all values are strings:
    if not all(isinstance(value, str) for value in target_ids):
        raise PathElementResolutionError(
            f"Cannot resolve path element '{path_element}' because the slot"
            + f" '{path_element.slot}' of resource '{source_resource}' contains"
            + " non-string values."
        )

    return target_ids


def resolve_path_element(
    *,
    source_resource: Json,
    global_metadata: Json,
    path_element: ReferencePathElement,
    anchor_points: dict[AnchorPoint],
) -> list[Json]:
    """Resolve a reference path element applied to a metadata resource.

    Returns:
        A list of metadata resources that are targeted by the path element.

    Raises:
        PathElementResolutionError:
            if the path element cannot be resolved.
    """

    target_ids = resolve_path_element_target_ids(
        source_resource=source_resource, path_element=path_element
    )

    raise NotImplementedError()


def transform_metadata_model(
    *, model: MetadataModel, references: list[InferredReference]
) -> MetadataModel:
    """Transform the metadata model and return the tranformed one.

    Raises:
            MetadataModelTransformationError:
                if the transformation of the metadata model fails.
    """

    for reference in references:
        model = add_reference_to_model(model=model, reference=reference)

    return model


def modify_metadata_resource(
    resource: Json,
    global_metadata: Json,
    reference: InferredReference,
    anchor_points: dict[AnchorPoint],
) -> Json:
    """Modify a metadata resource based on an inferred reference.

    Args:
        resource: The metadata resource to modify.
        global_metadata: The global metadata context to look up references in.
        reference: The inferred reference.
        anchor_points: The anchor points of the metadata model.

    Raises:
        MetadataTransformationError:
            if the transformation of the metadata fails.
    """


def add_reference_to_metadata(
    *, metadata: Json, reference: InferredReference, anchor_points: dict[AnchorPoint]
) -> Json:
    """Transform metadata by adding an inferred reference.

    Raises:
            MetadataTransformationError:
                if the transformation of the metadata fails.
    """


def transform_metadata(
    *, metadata: Json, model: MetadataModel, references: InferredReference
) -> Json:
    """Transform metadata and return the transformed one.

    Raises:
        MetadataTransformationError:
            if the transformation of the metadata fails.
    """

    anchor_points = get_anchors_by_target(model=model)

    for reference in references:
        metadata = add_reference_to_metadata(
            metadata=metadata, reference=reference, anchor_points=anchor_points
        )

    return metadata


class ReferenceInferenceConfig(ReferenceMapConfig):
    """Config parameters and their defaults."""


class ReferenceInferenceTransformation(TransformationBase):
    """A transformation to infer references based on existing ones in the metadata
    model."""

    def __init__(self, *, model: MetadataModel, config: ReferenceInferenceConfig):
        """Initialize the transformation with transformation-specific config params and
        the metadata model. The transformed model will be immediately available in the
        `transformed_model` attribute (may be a property).

        Raises:
            MetadataModelAssumptionError:
                if assumptions about the metadata model are not met.
            MetadataModelTransformationError:
                if the transformation of the metadata model fails.
        """

        self._original_model = model
        self._references_to_infer = config.inferred_references

        check_basic_model_assumption(model=model)

        self.transformed_model = transform_metadata_model(
            model=self._original_model, references=self._references_to_infer
        )

    def transform_metadata(self, metadata: Json) -> Json:
        """Transforms metadata and returns it.

        Raises:
            MetadataTransformationError:
                if the transformation of the metadata fails.
        """

        raise NotImplementedError()
