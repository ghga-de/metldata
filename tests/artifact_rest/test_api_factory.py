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

from metldata.artifacts_rest.artifact_info import ArtifactInfo
from metldata.artifacts_rest.api_factory import rest_api_factory
from tests.fixtures.artifact_info import EXAMPLE_ARTIFACT_INFOS


@pytest.mark.asyncio
async def get_example_app_client() -> TestClient:
    """Return a test client for a FastAPI generated using the artifact_rest_factory."""

    router = rest_api_factory(artifact_infos=EXAMPLE_ARTIFACT_INFOS)

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_artifacts_info_endpoint():
    """Test happy path of using the artifacts info endpoint."""

    expected_infos = EXAMPLE_ARTIFACT_INFOS

    client = await get_example_app_client()
    response = client.options("/artifacts")

    response_json = response.json()
    assert isinstance(response_json, list)
    observed_infos = [ArtifactInfo(**info) for info in response_json]
    assert observed_infos == expected_infos


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "artifact_name, expected_info",
    [(info.name, info) for info in EXAMPLE_ARTIFACT_INFOS],
)
async def test_artifact_info_endpoint(artifact_name: str, expected_info: ArtifactInfo):
    """Test happy path of using the artifact info endpoint."""

    client = await get_example_app_client()
    response = client.options(f"/artifacts/{artifact_name}")

    observed_info = ArtifactInfo(**response.json())
    assert observed_info == expected_info
