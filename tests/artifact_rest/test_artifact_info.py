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

"""Test the artifact_info module."""

from metldata.artifacts_rest.artifact_info import load_artifact_query_info
from tests.fixtures.metadata_models import MINIMAL_VALID_METADATA_MODEL


def test_load_artifact_query_info():
    """Test happy path of using load_artifact_query_info."""

    exptected_artifact_name = "test_artifact"
    exptected_artifact_description = "This is a test artifact."
    expected_queriable_class_names = {"File", "Dataset"}

    artifact_query_info = load_artifact_query_info(
        model=MINIMAL_VALID_METADATA_MODEL,
        name=exptected_artifact_name,
        description=exptected_artifact_description,
    )

    assert artifact_query_info.name == exptected_artifact_name
    assert artifact_query_info.description == exptected_artifact_description
    assert (
        artifact_query_info.queriable_classes.keys() == expected_queriable_class_names
    )
