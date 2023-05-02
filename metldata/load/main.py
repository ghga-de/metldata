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

"""Compose the main app and resolve dependencies."""

from functools import partial

from fastapi import FastAPI
from ghga_service_commons.api import configure_app
from hexkit.protocols.dao import DaoFactoryProtocol
from hexkit.providers.mongodb import MongoDbConfig
from motor.motor_asyncio import AsyncIOMotorClient

from metldata.load.api import rest_api_factory
from metldata.load.config import ArtifactLoaderAPIConfig


async def clear_database(config: MongoDbConfig):
    """Clear a mongodb database."""

    client = AsyncIOMotorClient(config.db_connection_str.get_secret_value())
    db = client[config.db_name]

    for collection_name in await db.list_collection_names():
        await db.drop_collection(collection_name)


async def get_app(
    config: ArtifactLoaderAPIConfig, dao_factory: DaoFactoryProtocol
) -> FastAPI:
    """Get the FastAPI app for loading artifacts. Performs dependency injection."""

    app = FastAPI(
        title="Artifacts Loader",
        description="Load artifacts into running services.",
    )
    configure_app(app=app, config=config)

    api_router = await rest_api_factory(
        artifact_infos=config.artifact_infos,
        dao_factory=dao_factory,
        token_hashes=config.loader_token_hashes,
        clear_database=partial(clear_database, config=config),
    )

    app.include_router(api_router)

    return app
