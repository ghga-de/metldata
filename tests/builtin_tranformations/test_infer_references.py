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
from tests.fixtures.metadata_models import ADVANCED_VALID_METADATA_MODEL


def test_transformation_active_happy():
    """Test the happy path of using the transformation with active inferred reference."""

    config = ReferenceInferenceConfig(
        inferred_ref_map={
            "Experiment": {
                "has_file": {
                    "path": "Experiment(has_sample)>Sample(has_file)>File",
                    "multivalued": True,
                }
            }
        }
    )

    original_model = ADVANCED_VALID_METADATA_MODEL
    transformation = ReferenceInferenceTransformation(
        model=original_model, config=config
    )
    transformed_model = transformation.transformed_model

    # check that the new slot exists:
    transformed_schema_view = transformed_model.schema_view
    new_slot = transformed_schema_view.induced_slot(
        slot_name="has_file", class_name="Experiment"
    )
    assert new_slot.range == "File"


def test_transformation_passive_happy():
    """Test the happy path of using the transformation with passive inferred reference."""

    config = ReferenceInferenceConfig(
        inferred_ref_map={
            "File": {
                "has_dataset": {
                    "path": "File<(has_file)Dataset",
                    "multivalued": True,
                }
            }
        }
    )

    original_model = ADVANCED_VALID_METADATA_MODEL
    transformation = ReferenceInferenceTransformation(
        model=original_model, config=config
    )
    transformed_model = transformation.transformed_model

    # check that the new slot exists:
    transformed_schema_view = transformed_model.schema_view
    new_slot = transformed_schema_view.induced_slot(
        slot_name="has_dataset", class_name="File"
    )
    assert new_slot.range == "Dataset"


def test_transformation_complex_happy():
    """Test the happy path of using the transformation with a complex inferred
    reference."""

    config = ReferenceInferenceConfig(
        inferred_ref_map={
            "Dataset": {
                "has_sample": {
                    "path": "Dataset(has_file)>File<(has_file)Sample",
                    "multivalued": True,
                }
            }
        }
    )

    original_model = ADVANCED_VALID_METADATA_MODEL
    transformation = ReferenceInferenceTransformation(
        model=original_model, config=config
    )
    transformed_model = transformation.transformed_model

    # check that the new slot exists:
    transformed_schema_view = transformed_model.schema_view
    new_slot = transformed_schema_view.induced_slot(
        slot_name="has_sample", class_name="Dataset"
    )
    assert new_slot.range == "Sample"
