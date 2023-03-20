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

from typing import cast

from linkml_runtime.linkml_model.meta import SlotDefinition

from metldata.model_utils.anchors import (
    AnchorPoint,
    AnchorPointNotFoundError,
    MetadataResourceNotFoundError,
    get_anchors_points_by_target,
    lookup_anchor_point,
    lookup_resource_by_identifier,
)
from metldata.model_utils.assumptions import check_basic_model_assumption
from metldata.model_utils.essentials import MetadataModel
from metldata.model_utils.manipulate import (
    ModelManipulationError,
    add_slot_if_not_exists,
    upsert_class_slot,
)
from metldata.reference.config import ReferenceMapConfig
from metldata.reference.path_elements import (
    ReferencePathElement,
    ReferencePathElementType,
)
from metldata.reference.reference import InferredReference
from metldata.transform.base import (
    Json,
    MetadataModelTransformationError,
    MetadataTransformationError,
    TransformationBase,
)


class SelfIdLookUpError(RuntimeError):
    """Raised when the self id cannot be looked up."""


class ForeignIdLookUpError(RuntimeError):
    """Raised when a foreign id cannot be looked up."""


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


def lookup_self_id(*, resource: Json, identifier_slot: str):
    """Lookup the ID of the specified resource."""

    self_id = resource.get(identifier_slot)

    if self_id is None:
        raise SelfIdLookUpError(
            "Cannot lookup the identifier because the corresponding slot"
            + f" '{identifier_slot}' is not present in the resource '{resource}'."
        )

    if not isinstance(self_id, str):
        raise SelfIdLookUpError(
            f"Cannot lookup the identifier because the slot '{identifier_slot}' of"
            + f" resource '{resource}' contains a non-string value."
        )

    return self_id


def lookup_foreign_ids(*, resource: Json, slot: str) -> list[str]:
    """Lookup foreing IDs referenced by the specified resource using the specified
    slot."""

    foreign_ids = resource.get(slot)

    if foreign_ids is None:
        raise ForeignIdLookUpError(
            f"Cannot lookup foreign IDs because the slot '{slot}' is not present"
            + f" in the resource '{resource}'."
        )

    # convert single value to list:
    if not isinstance(foreign_ids, list):
        foreign_ids = [foreign_ids]

    # check that all values are strings:
    if not all(isinstance(value, str) for value in foreign_ids):
        raise ForeignIdLookUpError(
            f"Cannot lookup foreign IDs because the slot '{slot}' of resource"
            + f" '{resource}' contains non-string values."
        )

    foreign_ids = cast(list[str], foreign_ids)

    return foreign_ids


def resolve_target_ids_active_element(
    *, source_resource: Json, path_element: ReferencePathElement
) -> list[str]:
    """Resolve an active reference path element applied to a metadata resource.

    Args:
        source_resource: The metadata resource to which the path element is applied.
        path_element: The active path element to resolve.

    Returns:
        A list of target IDs that are targeted by the path element in context of the
        provided source resource.

    Raises:
        PathElementResolutionError:
            if the path element cannot be resolved.
    """

    if path_element.type_ != ReferencePathElementType.ACTIVE:
        raise ValueError("Passive path element supplied where active expected.")

    try:
        target_ids = lookup_foreign_ids(
            resource=source_resource, slot=path_element.slot
        )
    except ForeignIdLookUpError as error:
        raise PathElementResolutionError(
            "Failed to resolve the path element applied to the"
            + f" resource '{source_resource}': {error}"
        ) from error

    return target_ids


def resolve_target_ids_passive_element(
    *,
    source_resource: Json,
    path_element: ReferencePathElement,
    global_metadata: Json,
    anchor_points_by_target: dict[str, AnchorPoint],
) -> list[str]:
    """Resolve a passive reference path element applied to a metadata resource.

    Args:
        source_resource: The metadata resource to which the path element is applied.
        path_element: The passive path element to resolve.
        global_metadata: The global metadata.
        anchor_points: The anchor points by target class.

    Returns:
        A list of target IDs that are targeted by the path element in context of the
        provided source resource.

    Raises:
        PathElementResolutionError:
            if the path element cannot be resolved.
    """

    if path_element.type_ != ReferencePathElementType.PASSIVE:
        raise ValueError("Active path element supplied where passive expected.")

    try:
        source_anchor_point = lookup_anchor_point(
            class_name=path_element.source,
            anchor_points_by_target=anchor_points_by_target,
        )
    except AnchorPointNotFoundError as error:
        raise PathElementResolutionError(
            "Cannot resolve path element because of a missing anchor point for"
            + f" source class '{path_element.source}'."
        ) from error

    try:
        source_idenifier = lookup_self_id(
            resource=source_resource,
            identifier_slot=source_anchor_point.identifier_slot,
        )
    except SelfIdLookUpError as error:
        raise PathElementResolutionError(
            f"Cannot resolve path element: '{error}'"
        ) from error

    # lookup the target resources:
    target_ids_of_interest: list[str] = []
    for target_id in global_metadata[path_element.target]:
        target_resource = lookup_resource_by_identifier(
            class_name=path_element.target,
            identifier=target_id,
            global_metadata=global_metadata,
            anchor_points_by_target=anchor_points_by_target,
        )

        referenced_source_ids = lookup_foreign_ids(
            resource=target_resource, slot=path_element.slot
        )

        if source_idenifier in referenced_source_ids:
            target_ids_of_interest.append(target_id)

    return target_ids_of_interest


def resolve_path_element(
    *,
    source_resource: Json,
    global_metadata: Json,
    path_element: ReferencePathElement,
    anchor_points_by_target: dict[str, AnchorPoint],
) -> list[Json]:
    """Resolve a reference path element applied to a metadata resource.

    Returns:
        A list of metadata resources that are targeted by the path element.

    Raises:
        PathElementResolutionError:
            if the path element cannot be resolved.
    """

    if path_element.type_ == ReferencePathElementType.ACTIVE:
        target_ids = resolve_target_ids_active_element(
            source_resource=source_resource, path_element=path_element
        )
    else:
        target_ids = resolve_target_ids_passive_element(
            source_resource=source_resource,
            path_element=path_element,
            global_metadata=global_metadata,
            anchor_points_by_target=anchor_points_by_target,
        )

    if not target_ids:
        raise PathElementResolutionError(
            f"Cannot resolve path element  for source resource '{source_resource}'"
            + " because no target resources were found."
        )

    target_resources: list[Json] = []
    for target_id in target_ids:
        try:
            target_resource = lookup_resource_by_identifier(
                class_name=path_element.target,
                identifier=target_id,
                global_metadata=global_metadata,
                anchor_points_by_target=anchor_points_by_target,
            )
        except MetadataResourceNotFoundError as error:
            raise PathElementResolutionError(
                f"Cannot resolve path element for source resource '{source_resource}'"
                + f" because the target resource with ID '{target_id}' could not be"
                + " found."
            ) from error
        target_resources.append(target_resource)

    return target_resources


def resolve_reference_for_metadata_resource(
    *,
    resource: Json,
    global_metadata: Json,
    reference: InferredReference,
    anchor_points_by_target: dict[str, AnchorPoint],
) -> list[Json]:
    """Resolve an inferred reference for an individual metadata resource.

    Args:
        resource: The metadata resource to resolve the reference for.
        global_metadata: The global metadata context to look up references in.
        reference: The inferred reference.
        anchor_points: The anchor points of the metadata model.

    Returns:
        A list of metadata resources that are targeted by the reference.

    Raises:
        MetadataTransformationError:
            if the transformation of the metadata fails.
    """

    source_resources = [resource]
    for path_element in reference.path.elements:
        target_resources: list[Json] = []
        for source_resource in source_resources:
            try:
                local_target_resources = resolve_path_element(
                    source_resource=source_resource,
                    global_metadata=global_metadata,
                    path_element=path_element,
                    anchor_points_by_target=anchor_points_by_target,
                )
            except PathElementResolutionError as error:
                raise MetadataTransformationError(
                    f"Cannot add reference '{reference}' to metadata resource"
                    + f" '{resource}' because the path element '{path_element}'"
                    + " could not be resolved."
                ) from error
            target_resources.extend(local_target_resources)

        # set the target resources of the current path element as the source resources
        # for the next path element:
        source_resources = target_resources

    return source_resources


def add_reference_to_metadata_resource(
    resource: Json,
    global_metadata: Json,
    reference: InferredReference,
    anchor_points_by_target: dict[str, AnchorPoint],
) -> Json:
    """Add an inferred reference to an individual metadata resource.

    Args:
        resource: The metadata resource to modify.
        global_metadata: The global metadata context to look up references in.
        reference: The inferred reference.
        anchor_points: The anchor points of the metadata model.

    Raises:
        MetadataTransformationError:
            if the transformation of the metadata fails.
    """

    try:
        target_anchor_point = lookup_anchor_point(
            class_name=reference.target, anchor_points_by_target=anchor_points_by_target
        )
    except AnchorPointNotFoundError as error:
        raise MetadataModelTransformationError(
            f"Cannot add reference '{reference}' to metadata resource '{resource}'"
            + " because the target anchor point could not be found."
        ) from error

    if reference.new_slot in resource:
        raise MetadataModelTransformationError(
            f"Cannot add reference '{reference}' to metadata resource '{resource}'"
            + f" because the target slot '{reference.new_slot}' already exists."
        )

    target_resources = resolve_reference_for_metadata_resource(
        resource=resource,
        global_metadata=global_metadata,
        reference=reference,
        anchor_points_by_target=anchor_points_by_target,
    )

    # get IDs of final target resources:
    target_ids: list[str] = []
    for target_resource in target_resources:
        try:
            target_ids.append(
                lookup_self_id(
                    resource=target_resource,
                    identifier_slot=target_anchor_point.identifier_slot,
                )
            )
        except SelfIdLookUpError as error:
            raise MetadataTransformationError(
                f"Cannot add reference '{reference}' to metadata resource '{resource}'"
                + f" because the target resource '{target_resource}' does not have"
                + f" an identifier in slot '{target_anchor_point.identifier_slot}'."
            ) from error

    # add the target IDs to the source resource:
    resource_copy = resource.copy()
    resource_copy[reference.new_slot] = target_ids

    return resource_copy


def add_reference_to_metadata(
    *,
    metadata: Json,
    reference: InferredReference,
    anchor_points_by_target: dict[str, AnchorPoint],
) -> Json:
    """Transform metadata by adding an inferred reference.

    Raises:
            MetadataTransformationError:
                if the transformation of the metadata fails.
    """

    try:
        source_anchor_point = lookup_anchor_point(
            class_name=reference.source, anchor_points_by_target=anchor_points_by_target
        )
    except AnchorPointNotFoundError as error:
        raise MetadataTransformationError(
            f"Cannot add reference '{reference}' to metadata because the source anchor"
            + " point could not be found."
        ) from error

    source_resources = metadata.get(source_anchor_point.root_slot)

    if not source_resources:
        raise MetadataTransformationError(
            f"Cannot add reference '{reference}' to metadata because the source anchor"
            + f" point '{source_anchor_point.root_slot}' does not exist in the"
            + " metadata."
        )

    modified_source_resources = [
        add_reference_to_metadata_resource(
            resource=source_resource,
            global_metadata=metadata,
            reference=reference,
            anchor_points_by_target=anchor_points_by_target,
        )
        for source_resource in source_resources
    ]

    metadata_copy = metadata.copy()
    metadata_copy[source_anchor_point.root_slot] = modified_source_resources

    return metadata_copy


def transform_metadata(
    *, metadata: Json, model: MetadataModel, references: list[InferredReference]
) -> Json:
    """Transform metadata and return the transformed one.

    Raises:
        MetadataTransformationError:
            if the transformation of the metadata fails.
    """

    anchor_points_by_target = get_anchors_points_by_target(model=model)

    for reference in references:
        metadata = add_reference_to_metadata(
            metadata=metadata,
            reference=reference,
            anchor_points_by_target=anchor_points_by_target,
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
        self._inferred_references = config.inferred_references

        check_basic_model_assumption(model=model)

        self.transformed_model = transform_metadata_model(
            model=self._original_model, references=self._inferred_references
        )

    def transform_metadata(self, metadata: Json) -> Json:
        """Transforms metadata and returns it.

        Raises:
            MetadataTransformationError:
                if the transformation of the metadata fails.
        """

        return transform_metadata(
            metadata=metadata,
            model=self.transformed_model,
            references=self._inferred_references,
        )
