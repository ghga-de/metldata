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

"""Joint fixture with setup for event content"""

import json
from dataclasses import dataclass
from typing import Any

from ghga_service_commons.api.testing import AsyncTestClient
from hexkit.providers.akafka.testutils import KafkaFixture
from hexkit.providers.mongodb.testutils import MongoDbFixture
from pytest_asyncio import fixture

from metldata.artifacts_rest.artifact_info import ArtifactInfo, load_artifact_info
from metldata.custom_types import Json
from metldata.load.auth import generate_token_and_hash
from metldata.load.config import ArtifactLoaderAPIConfig
from metldata.load.main import get_app
from metldata.load.models import ArtifactJson, ArtifactResourceDict
from metldata.model_utils.essentials import MetadataModel
from tests.fixtures.load.config import get_config
from tests.fixtures.load.utils import BASE_DIR

ARTIFACT_INFOS_PATH = BASE_DIR / "example_models" / "artifact_infos.json"
ARTIFACT_NAME = "embedded_public"
EMBEDDED_ARTIFACT_PATH = BASE_DIR / "example_metadata" / f"{ARTIFACT_NAME}.json"
ADDED_ACCESSIONS_PATH = BASE_DIR / "example_metadata" / "added_accessions.json"
STATS_PUBLIC_PATH = BASE_DIR / "example_metadata" / "stats_public.json"
EMBEDDED_DATASET_TEST_PATH = BASE_DIR / "example_metadata" / "embedded_dataset.json"
EMBEDDED_ARTIFACT_MODEL_PATH = (
    BASE_DIR / "example_models" / f"{ARTIFACT_NAME}_model.yaml"
)
ADDED_ACCESSIONS_MODEL_PATH = (
    BASE_DIR / "example_models" / "added_accessions_model.yaml"
)
STATS_PUBLIC_MODEL_PATH = BASE_DIR / "example_models" / "stats_public_model.yaml"


@dataclass
class JointFixture:
    """Joint fixture for testing"""

    artifact_infos: list[ArtifactInfo]
    artifact_resources: dict[str, Any]
    client: AsyncTestClient
    config: ArtifactLoaderAPIConfig
    expected_file_resource_content: Json
    expected_embedded_dataset_resource_content: Json
    kafka: KafkaFixture
    mongodb: MongoDbFixture
    token: str


@fixture
async def joint_fixture(kafka: KafkaFixture, mongodb: MongoDbFixture) -> JointFixture:
    """Get a tuple of a configured test client together with a corresponding token."""
    artifact_infos = [
        load_artifact_info(
            name=ARTIFACT_NAME,
            description=ARTIFACT_NAME,
            model=MetadataModel.init_from_path(EMBEDDED_ARTIFACT_MODEL_PATH),
        ),
        load_artifact_info(
            name="added_accessions",
            description="added_accessions",
            model=MetadataModel.init_from_path(ADDED_ACCESSIONS_MODEL_PATH),
        ),
        load_artifact_info(
            name="stats_public",
            description="stats_public",
            model=MetadataModel.init_from_path(STATS_PUBLIC_MODEL_PATH),
        ),
    ]

    with open(EMBEDDED_ARTIFACT_PATH, encoding="utf-8") as file:
        raw_artifacts = json.load(file)
        artifacts: ArtifactResourceDict = {
            raw_artifacts["type_"]: [
                ArtifactJson(
                    artifact_name=raw_artifacts["type_"],
                    study_accession="",
                    content=raw_artifacts["payload"]["content"],
                )
            ]
        }

    with open(ADDED_ACCESSIONS_PATH, encoding="utf-8") as file:
        added_accessions_artifact = json.load(file)
        artifacts[added_accessions_artifact["type_"]] = [
            ArtifactJson(
                artifact_name=added_accessions_artifact["type_"],
                study_accession=added_accessions_artifact["payload"]["content"][
                    "studies"
                ][0]["accession"],
                content=added_accessions_artifact["payload"]["content"],
            )
        ]

    with open(STATS_PUBLIC_PATH, encoding="utf-8") as file:
        stats_public_artifact = json.load(file)
        artifacts[stats_public_artifact["type_"]] = [
            ArtifactJson(
                artifact_name=stats_public_artifact["type_"],
                study_accession="",
                content=stats_public_artifact["payload"]["content"],
            )
        ]

    token, token_hash = generate_token_and_hash()

    config = get_config(
        [
            {
                "artifact_infos": artifact_infos,
                "loader_token_hashes": [token_hash],
            },
            kafka.config,
            mongodb.config,
        ]
    )

    expected_file_resource_content = artifacts["embedded_public"][0]["content"][
        "study_files"
    ][0]
    expected_embedded_dataset_resource_content = artifacts["embedded_public"][0][
        "content"
    ]["embedded_dataset"][1]

    app = await get_app(config=config)
    client = AsyncTestClient(app)
    return JointFixture(
        artifact_infos=artifact_infos,
        artifact_resources=artifacts,
        client=client,
        config=config,
        expected_file_resource_content=expected_file_resource_content,
        expected_embedded_dataset_resource_content=expected_embedded_dataset_resource_content,
        kafka=kafka,
        mongodb=mongodb,
        token=token,
    )
