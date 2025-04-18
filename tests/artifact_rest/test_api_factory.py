# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Test the api_factory module."""

import httpx
import pytest
from fastapi import FastAPI
from ghga_service_commons.api.testing import AsyncTestClient
from ghga_service_commons.utils.utc_dates import UTCDatetime, now_as_utc
from hexkit.protocols.dao import DaoFactoryProtocol
from hexkit.providers.mongodb.testutils import MongoDbFixture

from metldata.artifacts_rest.api_factory import rest_api_factory
from metldata.artifacts_rest.artifact_info import ArtifactInfo, get_artifact_info_dict
from metldata.load.aggregator import MongoDbAggregator
from metldata.load.stats import create_stats_using_aggregator
from tests.artifact_rest.test_load_artifacts import load_example_artifact_resources
from tests.fixtures.artifact_info import EXAMPLE_ARTIFACT_INFOS, MINIMAL_ARTIFACT_INFO

pytestmark = pytest.mark.asyncio()


async def get_example_app_client(
    dao_factory: DaoFactoryProtocol,
    artifact_infos: list[ArtifactInfo] = EXAMPLE_ARTIFACT_INFOS,
) -> httpx.AsyncClient:
    """Return a test client for a FastAPI generated using the artifact_rest_factory."""
    router = await rest_api_factory(
        artifact_infos=artifact_infos, dao_factory=dao_factory
    )

    app = FastAPI()
    app.include_router(router)
    return AsyncTestClient(app)


async def test_health_check(mongodb: MongoDbFixture):
    """Test that the health check endpoint works."""
    async with await get_example_app_client(dao_factory=mongodb.dao_factory) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


async def test_artifacts_info_endpoint(mongodb: MongoDbFixture):
    """Test happy path of using the artifacts info endpoint."""
    expected_infos = EXAMPLE_ARTIFACT_INFOS

    async with await get_example_app_client(dao_factory=mongodb.dao_factory) as client:
        response = await client.options("/artifacts")

    response_json = response.json()
    assert isinstance(response_json, list)
    observed_infos = [ArtifactInfo(**info) for info in response_json]
    assert observed_infos == expected_infos


@pytest.mark.parametrize(
    "artifact_name, expected_info",
    [(info.name, info) for info in EXAMPLE_ARTIFACT_INFOS],
)
async def test_artifact_info_endpoint(
    artifact_name: str,
    expected_info: ArtifactInfo,
    mongodb: MongoDbFixture,
):
    """Test happy path of using the artifact info endpoint."""
    async with await get_example_app_client(dao_factory=mongodb.dao_factory) as client:
        response = await client.options(f"/artifacts/{artifact_name}")

    observed_info = ArtifactInfo(**response.json())
    assert observed_info == expected_info


async def test_get_artifact_resource_endpoint(mongodb: MongoDbFixture):
    """Test happy path of using the get artifact resource endpoint."""
    # load example resources and prepare client:
    await load_example_artifact_resources(dao_factory=mongodb.dao_factory)

    # Get an example resource:
    artifact_name = MINIMAL_ARTIFACT_INFO.name
    class_name = "File"
    resource_id = "test_sample_01_R1"
    async with await get_example_app_client(
        dao_factory=mongodb.dao_factory,
        artifact_infos=[MINIMAL_ARTIFACT_INFO],
    ) as client:
        response = await client.get(
            f"/artifacts/{artifact_name}/classes/{class_name}/resources/{resource_id}"
        )

    assert response.status_code == 200
    observed_resource = response.json()
    # check that the right object was return using an example slot:
    expected_checksum = (
        "1c8aed294d5dec3740a175f6b655725fa668bfe41311e74f7ca9d85c91371b4e"
    )
    assert observed_resource["checksum"] == expected_checksum
    # check that the ID is included in the resource:
    assert observed_resource["alias"] == resource_id


async def test_get_stats_endpoint(mongodb: MongoDbFixture):
    """Test happy path of using the get stats endpoint."""
    # load example resources and prepare client:
    await load_example_artifact_resources(dao_factory=mongodb.dao_factory)

    artifact_infos = [MINIMAL_ARTIFACT_INFO]

    await create_stats_using_aggregator(
        artifact_infos=get_artifact_info_dict(artifact_infos=artifact_infos),
        primary_artifact_name=artifact_infos[-1].name,
        db_aggregator=MongoDbAggregator(config=mongodb.config),
    )

    # Get the global summary statistics:
    async with await get_example_app_client(
        dao_factory=mongodb.dao_factory,
        artifact_infos=artifact_infos,
    ) as client:
        response = await client.get("/stats")

    assert response.status_code == 200
    observed_stats = response.json()
    assert isinstance(observed_stats, dict)

    raw_observed_created = observed_stats.pop("created")
    if isinstance(raw_observed_created, str) and raw_observed_created.endswith("Z"):
        raw_observed_created = raw_observed_created.replace("Z", "+00:00")

    observed_created = UTCDatetime.fromisoformat(raw_observed_created)
    assert abs((now_as_utc() - observed_created).seconds) < 5

    expected_stats = {
        "id": "global",
        "resource_stats": {
            "Dataset": {"count": 2},
            "File": {"count": 4, "stats": {"format": [{"value": "fastq", "count": 4}]}},
        },
    }
    assert observed_stats == expected_stats
