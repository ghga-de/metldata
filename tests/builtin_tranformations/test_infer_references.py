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

"""Test the infer_references module."""

from metldata.builtin_transformations.infer_references import (
    ReferenceInferenceConfig,
    ReferenceInferenceTransformation,
)
from metldata.model_utils.essentials import MetadataModel
from tests.fixtures.metadata_models import ADVANCED_VALID_METADATA_MODEL


def test_transformation_active_happy():
    """Test the happy path of using the transformation with active inferred reference."""

    config = ReferenceInferenceConfig(
        inferred_ref_map={
            "Experiment": {
                "has file": {
                    "path": "Experiment(has sample)>Sample(has file)>File",
                    "multivalued": True,
                }
            }
        }
    )

    original_model = MetadataModel.init_from_path(ADVANCED_VALID_METADATA_MODEL)
    transformation = ReferenceInferenceTransformation(
        model=original_model, config=config
    )
    transformed_model = transformation.transformed_model

    # check that the new slot exists:
    transformed_schema_view = transformed_model.schema_view
    new_slot = transformed_schema_view.induced_slot(
        slot_name="has file", class_name="Experiment"
    )
    assert new_slot.range == "File"


def test_transformation_passive_happy():
    """Test the happy path of using the transformation with passive inferred reference."""

    config = ReferenceInferenceConfig(
        inferred_ref_map={
            "File": {
                "has dataset": {
                    "path": "File<(has file)Dataset",
                    "multivalued": True,
                }
            }
        }
    )

    original_model = MetadataModel.init_from_path(ADVANCED_VALID_METADATA_MODEL)
    transformation = ReferenceInferenceTransformation(
        model=original_model, config=config
    )
    transformed_model = transformation.transformed_model

    # check that the new slot exists:
    transformed_schema_view = transformed_model.schema_view
    new_slot = transformed_schema_view.induced_slot(
        slot_name="has dataset", class_name="File"
    )
    assert new_slot.range == "Dataset"


def test_transformation_complex_happy():
    """Test the happy path of using the transformation with a complex inferred
    reference."""

    config = ReferenceInferenceConfig(
        inferred_ref_map={
            "Dataset": {
                "has sample": {
                    "path": "Dataset(has file)>File<(has file)Sample",
                    "multivalued": True,
                }
            }
        }
    )

    original_model = MetadataModel.init_from_path(ADVANCED_VALID_METADATA_MODEL)
    transformation = ReferenceInferenceTransformation(
        model=original_model, config=config
    )
    transformed_model = transformation.transformed_model

    # check that the new slot exists:
    transformed_schema_view = transformed_model.schema_view
    new_slot = transformed_schema_view.induced_slot(
        slot_name="has sample", class_name="Dataset"
    )
    assert new_slot.range == "Sample"
