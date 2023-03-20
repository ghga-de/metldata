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

"""Test the anchor module."""


import pytest

from metldata.model_utils.anchors import (
    AnchorPoint,
    AnchorPointNotFoundError,
    InvalidAnchorPointError,
    MetadataResourceNotFoundError,
    filter_anchor_points,
    get_anchor_points,
    get_anchors_points_by_target,
    lookup_anchor_point,
    lookup_resource_by_identifier,
)
from metldata.model_utils.essentials import MetadataModel
from tests.fixtures.metadata import VALID_MINIMAL_METADATA_EXAMPLE
from tests.fixtures.metadata_models import (
    ANCHORS_INVALID_MODELS,
    MINIMAL_VALID_METADATA_MODEL,
)

EXAMPLE_ANCHOR_POINTS = {
    AnchorPoint(target_class="File", identifier_slot="alias", root_slot="has_file"),
    AnchorPoint(
        target_class="Dataset", identifier_slot="alias", root_slot="has_dataset"
    ),
}

EXAMPLE_ANCHOR_POINTS_BY_TARGET = {
    "File": AnchorPoint(
        target_class="File", identifier_slot="alias", root_slot="has_file"
    ),
    "Dataset": AnchorPoint(
        target_class="Dataset", identifier_slot="alias", root_slot="has_dataset"
    ),
}


def test_get_anchor_points_happy():
    """Test the happy path of using the get_anchor_points function."""

    expected_anchor_points = EXAMPLE_ANCHOR_POINTS

    observed_anchor_points = get_anchor_points(model=MINIMAL_VALID_METADATA_MODEL)

    assert observed_anchor_points == expected_anchor_points


@pytest.mark.parametrize("invalid_model", ANCHORS_INVALID_MODELS)
def test_get_anchor_points_invalid(invalid_model: MetadataModel):
    """Test the get_anchor_points function for models with invalid anchor points."""

    with pytest.raises(InvalidAnchorPointError):
        _ = get_anchor_points(model=invalid_model)


def test_get_anchor_points_by_target_happy():
    """Test the happy path of using the get_anchors_by_target function."""

    expected_anchor_points = EXAMPLE_ANCHOR_POINTS_BY_TARGET

    observed_anchor_points = get_anchors_points_by_target(
        model=MINIMAL_VALID_METADATA_MODEL
    )

    assert observed_anchor_points == expected_anchor_points


def test_filter_anchor_points_happy():
    """Test the happy path of using the filter_anchor_points function."""

    class_of_interest = "File"
    expected_anchor_points = {
        class_of_interest: EXAMPLE_ANCHOR_POINTS_BY_TARGET[class_of_interest],
    }

    observed_anchor_points = filter_anchor_points(
        anchor_points_by_target=EXAMPLE_ANCHOR_POINTS_BY_TARGET,
        classes_of_interest={class_of_interest},
    )

    assert observed_anchor_points == expected_anchor_points


def test_filter_anchor_points_non_existing_class():
    """Test the happy path of using the filter_anchor_points function."""

    classes_of_interest = set(EXAMPLE_ANCHOR_POINTS_BY_TARGET.keys())
    classes_of_interest.add("NonExisting")

    with pytest.raises(AnchorPointNotFoundError):
        _ = filter_anchor_points(
            anchor_points_by_target=EXAMPLE_ANCHOR_POINTS_BY_TARGET,
            classes_of_interest=classes_of_interest,
        )


def test_lookup_resource_by_identifier_happy():
    """Test the happy path of using the lookup_resource_by_identifier function."""

    identifier = "test_sample_01_R1"
    expected_resource = VALID_MINIMAL_METADATA_EXAMPLE["has_file"][identifier]
    expected_resource["alias"] = identifier

    anchor_points_by_target = get_anchors_points_by_target(
        model=MINIMAL_VALID_METADATA_MODEL
    )
    observed_resource = lookup_resource_by_identifier(
        class_name="File",
        global_metadata=VALID_MINIMAL_METADATA_EXAMPLE,
        identifier=identifier,
        anchor_points_by_target=anchor_points_by_target,
    )

    assert observed_resource == expected_resource


def test_lookup_resource_by_identifier_not_exist():
    """Test the using the lookup_resource_by_identifier function with an identifier
    that does not exist."""

    identifier = "non_existing_identifier"

    anchor_points_by_target = get_anchors_points_by_target(
        model=MINIMAL_VALID_METADATA_MODEL
    )

    with pytest.raises(MetadataResourceNotFoundError):
        _ = lookup_resource_by_identifier(
            class_name="File",
            global_metadata=VALID_MINIMAL_METADATA_EXAMPLE,
            identifier=identifier,
            anchor_points_by_target=anchor_points_by_target,
        )


def test_lookup_anchor_point_happy():
    """Test the happy path of using the lookup_anchor_point function."""

    class_name = "File"
    expected_anchor_point = EXAMPLE_ANCHOR_POINTS_BY_TARGET[class_name]

    observed_anchor_point = lookup_anchor_point(
        class_name=class_name, anchor_points_by_target=EXAMPLE_ANCHOR_POINTS_BY_TARGET
    )

    assert observed_anchor_point == expected_anchor_point


def test_lookup_anchor_point_not_found():
    """Test the using the lookup_anchor_point function with a class name that does
    not exist."""

    with pytest.raises(AnchorPointNotFoundError):
        _ = lookup_anchor_point(
            class_name="NonExisting",
            anchor_points_by_target=EXAMPLE_ANCHOR_POINTS_BY_TARGET,
        )
