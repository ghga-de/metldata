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

"""Test the factory module."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from metldata.artifacts_rest.artifact_info import ArtifactQueryInfo
from metldata.artifacts_rest.factory import artifact_rest_factory
from tests.fixtures.artifact_query_info import EXAMPLE_ARTIFACT_QUERY_INFOS


def get_example_app_client() -> TestClient:
    """Return a test client for a FastAPI generated using the artifact_rest_factory."""

    router = artifact_rest_factory(artifact_infos=EXAMPLE_ARTIFACT_QUERY_INFOS)

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_artifacts_info_endpoint():
    """Test happy path of using the artifacts info endpoint."""

    expected_query_infos = EXAMPLE_ARTIFACT_QUERY_INFOS

    client = get_example_app_client()
    response = client.options("/artifacts")

    response_json = response.json()
    assert isinstance(response_json, list)
    observed_query_infos = [
        ArtifactQueryInfo(**query_info) for query_info in response_json
    ]
    assert observed_query_infos == expected_query_infos


@pytest.mark.parametrize(
    "artifact_name, expected_query_info",
    [(query_info.name, query_info) for query_info in EXAMPLE_ARTIFACT_QUERY_INFOS],
)
def test_artifact_info_endpoint(
    artifact_name: str, expected_query_info: ArtifactQueryInfo
):
    """Test happy path of using the artifact info endpoint."""

    client = get_example_app_client()
    response = client.options(f"/artifacts/{artifact_name}")

    observed_query_info = ArtifactQueryInfo(**response.json())
    assert observed_query_info == expected_query_info
