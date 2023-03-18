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

from pathlib import Path

import pytest

from metldata.model_utils.anchors import (
    AnchorPoint,
    InvalidAnchorPointError,
    get_anchor_points,
)
from metldata.model_utils.essentials import MetadataModel
from tests.fixtures.metadata_models import (
    ANCHORS_INVALID_MODELS,
    MINIMAL_VALID_METADATA_MODEL,
)


def test_get_anchor_points_happy():
    """Test the happy path of using the get_anchor_points function."""

    expected_anchor_points = {
        AnchorPoint(target_class="File", identifier_slot="alias", root_slot="has file"),
        AnchorPoint(
            target_class="Dataset", identifier_slot="alias", root_slot="has dataset"
        ),
    }

    model = MetadataModel.init_from_path(MINIMAL_VALID_METADATA_MODEL)
    observed_anchor_points = get_anchor_points(model=model)

    assert observed_anchor_points == expected_anchor_points


@pytest.mark.parametrize("invalid_model", ANCHORS_INVALID_MODELS)
def test_get_anchor_points_invalid(invalid_model: Path):
    """Test the get_anchor_points function for models with invalid anchor points."""

    model = MetadataModel.init_from_path(invalid_model)

    with pytest.raises(InvalidAnchorPointError):
        _ = get_anchor_points(model=model)
