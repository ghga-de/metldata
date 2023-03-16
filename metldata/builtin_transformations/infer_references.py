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

from metldata.model_utils.assumptions import check_basic_model_assumption
from metldata.model_utils.essentials import MetadataModel
from metldata.model_utils.manipulate import add_slot_if_not_exists, upsert_class_slot
from metldata.reference.config import ReferenceMapConfig
from metldata.reference.reference import InferredReference
from metldata.transform.base import Json, TransformationBase


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
    added."""

    new_slot = inferred_reference_to_slot(reference)

    schema_view = model.schema_view
    schema_view = add_slot_if_not_exists(schema_view=schema_view, new_slot=new_slot)
    schema_view = upsert_class_slot(
        schema_view=schema_view, class_name=reference.source, new_slot=new_slot
    )

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
