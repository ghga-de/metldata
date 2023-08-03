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

"""Joint fixture with setup for event content"""


from dataclasses import dataclass

from ghga_service_commons.api.testing import AsyncTestClient
from hexkit.providers.akafka.testutils import kafka_fixture, KafkaFixture
from pydantic import BaseSettings
from pytest_asyncio import fixture

from metldata.artifacts_rest.models import ArtifactInfo
from metldata.load.auth import generate_token_and_hash
from metldata.load.main import get_app
from tests.fixtures.artifact_info import EXAMPLE_ARTIFACT_INFOS
from tests.fixtures.load.config import get_config
from tests.fixtures.mongodb import (  # noqa: F401; pylint: disable=unused-import
    MongoDbFixture,
    mongodb_fixture,
)


@dataclass
class JointFixture:
    client: AsyncTestClient
    mongodb: MongoDbFixture
    token: str


@fixture
async def joint_fixture(
    kafka_fixture: KafkaFixture,
    mongodb_fixture: MongoDbFixture,  # noqa: F811
) -> JointFixture:
    """Get a tuple of a configured test client together with a corresponding token."""

    token, token_hash = generate_token_and_hash()

    config = get_config(
        [
            {
                "artifact_infos": EXAMPLE_ARTIFACT_INFOS,
                "loader_token_hashes": [token_hash],
            },
            kafka_fixture.config,
            mongodb_fixture.config,
        ]
    )
    app = await get_app(config=config)
    client = AsyncTestClient(app)
    return JointFixture(client=client, mongodb=mongodb_fixture, token=token)
